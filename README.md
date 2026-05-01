# 🔬 BugRadar AI

> AI-powered Python bug detection using **CodeBERT**, **PyTorch** and a **multi-step LangGraph agent**

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?style=flat-square&logo=fastapi)
![PyTorch](https://img.shields.io/badge/PyTorch-2.3-red?style=flat-square&logo=pytorch)
![React](https://img.shields.io/badge/React-18-cyan?style=flat-square&logo=react)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent-purple?style=flat-square)

---

## 📌 What is BugRadar AI?

BugRadar AI is a final year project that scans any public Python GitHub repository and predicts the **bug probability of every file** using a custom-trained deep learning model. On top of the ML prediction, a **4-step LangGraph AI agent** then explains exactly what is wrong, generates a fix, and writes unit tests.

---

## 🏗️ Architecture

```
GitHub Repo URL
      │
      ▼
┌─────────────────────┐
│   github_utils.py   │  ← shallow git clone, extract all .py files
└─────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────┐
│                ml_model.py                  │
│                                             │
│  CodeBERT (microsoft/codebert-base)         │
│  → 768-dim CLS embedding per file           │
│                                             │
│  Radon → LOC + avg cyclomatic complexity    │
│  → 2 tabular features (StandardScaler)      │
│                                             │
│  BugClassifier (PyTorch, 770→512→256→1)     │
│  → sigmoid → bug probability %              │
└─────────────────────────────────────────────┘
      │  (high probability files)
      ▼
┌─────────────────────────────────────────────┐
│              llm_retriwer.py                │
│         (LangGraph 5-node agent)            │
│                                             │
│  Node 1: Hypothesize  → bug category guess  │
│  Node 2: Critique     → specific issues     │
│  Node 3: Fix          → corrected code      │
│  Node 4: Tests        → pytest cases        │
│  Node 5: Report       → full markdown       │
└─────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────┐
│     FastAPI         │  ← REST API with JWT auth
│     main.py         │
└─────────────────────┘
      │
      ▼
┌─────────────────────┐
│  React Frontend     │  ← Bar chart, scatter, heatmap, AI chat
│  index.html         │
└─────────────────────┘
```

---

## ✨ Features

- 🔐 **JWT Authentication** — Secure signup/login with bcrypt password hashing
- 🤖 **CodeBERT Embeddings** — Microsoft's code-pretrained RoBERTa model for semantic file understanding
- 🧠 **Custom PyTorch Model** — Trained BugClassifier (770→512→256→1) with BatchNorm + Dropout
- 🔗 **LangGraph Agent** — 4-step sequential agent: Hypothesis → Critique → Fix → Tests
- 📊 **3 Chart Types** — Bar chart, LOC vs Risk scatter, Directory heatmap
- 💬 **AI Chat Assistant** — Ask questions about your scan results
- ⚡ **FastAPI Backend** — Async, typed, with CORS and JWT middleware

---

## 📁 Project Structure

```
project/
├── backend/
│   ├── main.py           # FastAPI app — routes, CORS, JWT protection
│   ├── auth.py           # Signup, login, token creation/verification
│   ├── ml_model.py       # BugPredictor: CodeBERT + BugClassifier
│   ├── github_utils.py   # Clone repo, extract .py files
│   └── llm_retriwer.py   # LangGraph 5-node code review agent
├── frontend/
│   └── react/
│       └── index.html    # Single-file React app (no build step)
├── models/
│   ├── best_bug_model.pth  # Trained PyTorch weights
│   └── scaler.pkl          # Fitted StandardScaler
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/bugradar-ai.git
cd bugradar-ai
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file in the project root:
```
HUGGINGFACEHUB_API_TOKEN=hf_your_token_here
JWT_SECRET_KEY=your-secret-key-here
```
Get your HuggingFace token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### 4. Start the backend
```bash
uvicorn backend.main:app --reload
```

### 5. Open the frontend
```bash
open frontend/react/index.html
```
Or just double-click `index.html` in Finder.

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/signup` | ❌ | Register a new user |
| POST | `/auth/login` | ❌ | Login, receive JWT token |
| GET | `/auth/me` | ✅ | Get current user from token |
| POST | `/analyze` | ✅ | Scan a GitHub repo |
| POST | `/review` | ✅ | Run LangGraph agent on a file |
| GET | `/health` | ❌ | Health check |

---

## 🧠 ML Model Details

| Component | Detail |
|-----------|--------|
| Base model | `microsoft/codebert-base` (RoBERTa) |
| Embedding | 768-dim CLS token |
| Extra features | LOC, avg cyclomatic complexity (radon) |
| Total input | 770 features |
| Architecture | Linear(770→512) → BN → ReLU → Dropout(0.3) → Linear(512→256) → BN → ReLU → Dropout(0.3) → Linear(256→1) |
| Output | Sigmoid → bug probability (0–100%) |
| Loss | BCEWithLogitsLoss |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vanilla JS (no build step) |
| Backend | FastAPI, Uvicorn |
| ML | PyTorch, Transformers (CodeBERT), scikit-learn, Radon |
| LLM Agent | LangGraph, LangChain, HuggingFace Inference API |
| Auth | JWT (PyJWT), bcrypt |
| Data | Git clone via GitPython |

---

## 📸 Screenshots

> *(Add screenshots of your login page, dashboard, chart views, and AI review modal)*

---

## 👨‍💻 Author

**Jaish Kumar**
Final Year Project — B.Tech Computer Science


