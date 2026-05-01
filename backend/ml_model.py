import os
import torch
import torch.nn as nn
import pickle
import numpy as np
from pathlib import Path
from transformers import RobertaTokenizer, RobertaModel
from radon.complexity import cc_visit

# ── Path resolution ───────────────────────────────────────────────────────────

_HERE       = Path(__file__).resolve().parent
MODELS_DIR  = _HERE / ".." / "models"
SCALER_PATH = MODELS_DIR / "scaler.pkl"
MODEL_PATH  = MODELS_DIR / "best_bug_model.pth"


# ── Neural network architecture ───────────────────────────────────────────────

class BugClassifier(nn.Module):
    def __init__(self, input_dim: int = 770):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 512),
            nn.BatchNorm1d(512),  
            nn.ReLU(),
            nn.Dropout(0.3),       
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 1),    
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


# ── Predictor ───────────────────────────────────
class BugPredictor:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        
        if not SCALER_PATH.exists():
            raise FileNotFoundError(f"Scaler not found at {SCALER_PATH}")
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model weights not found at {MODEL_PATH}")

        
        with open(SCALER_PATH, "rb") as f:
            self.scaler = pickle.load(f)

     
        print("Loading CodeBERT…")
        self.tokenizer = RobertaTokenizer.from_pretrained("microsoft/codebert-base")
        self.codebert  = RobertaModel.from_pretrained("microsoft/codebert-base").to(self.device)
        self.codebert.eval()  

       
        self.model = BugClassifier(input_dim=770).to(self.device)
        self.model.load_state_dict(
            torch.load(MODEL_PATH, map_location=self.device, weights_only=True)
        )
        self.model.eval()  

    def get_codebert_embedding(self, code_string: str) -> np.ndarray:
       
        inputs = self.tokenizer(
            code_string,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        ).to(self.device)

        with torch.no_grad():
            outputs = self.codebert(**inputs)
            # last_hidden_state shape: [1, seq_len, 768]
            # [:, 0, :] picks the CLS token → shape [1, 768] → squeeze to [768]
            return outputs.last_hidden_state[:, 0, :].cpu().numpy()[0]

    def get_tabular_features(self, code_string: str) -> np.ndarray:
        """
        Extract 2 simple code-quality metrics:
          - LOC: lines of code (raw count, including blanks/comments)
          - avg_complexity: average cyclomatic complexity across all functions
            (1 = straight-line, higher = more branches → harder to reason about)
        Returns shape [1, 2] so sklearn's scaler.transform() works directly.
        """
        loc = len(code_string.splitlines())
        complexity = 1.0   # default: no functions found = trivially simple
        try:
            blocks = cc_visit(code_string)   # radon: parse every function/method
            if blocks:
                complexity = sum(b.complexity for b in blocks) / len(blocks)
        except Exception:
            pass  # syntax errors in target code — keep default

        return np.array([[loc, complexity]], dtype=np.float64)

    def predict(self, files_dict: dict) -> list:
        """
        For every file in the dict:
          1. Get 768-dim CodeBERT embedding
          2. Get 2 tabular features, scale them
          3. Concatenate → 770-dim feature vector
          4. Run through BugClassifier → sigmoid → bug probability %
        Returns a list of dicts sorted by the caller (main.py).
        """
        results = []

        for file_path, code in files_dict.items():
            # Step 1 — semantic embedding
            embedding = self.get_codebert_embedding(code)

            # Step 2 — tabular features (scaled to match training distribution)
            raw_tab    = self.get_tabular_features(code)
            scaled_tab = self.scaler.transform(raw_tab)[0]

            # Step 3 — combine into one 770-dim vector
            combined = np.hstack([embedding, scaled_tab])
            tensor   = torch.FloatTensor(combined).unsqueeze(0).to(self.device)  # [1, 770]

            # Step 4 — inference
            with torch.no_grad():
                logit       = self.model(tensor).squeeze()            # raw score
                probability = torch.sigmoid(logit).item()          # 0 → 1 

            results.append({
                "file":            file_path,
                "bug_probability": round(probability * 100, 2),       # 0 → 100 %
                "loc":             int(raw_tab[0][0]),
            })

        return results
