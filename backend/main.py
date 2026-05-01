from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from github_utils import extract_python_files
from ml_model import BugPredictor
from llm_retriwer import run_code_review
from auth import signup, login, get_current_user

app = FastAPI(title="BugRadar AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "null",  
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = BugPredictor()


# ── Auth schemas ──────────────────────────────────────────────────────────────
class SignupRequest(BaseModel):
    email: str
    name: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


# ── Auth endpoints ────────────────────────────────────────────────────────────
@app.post("/auth/signup")
def auth_signup(req: SignupRequest):
    """Register a new user, return JWT token."""
    return signup(req.email, req.name, req.password)


@app.post("/auth/login")
def auth_login(req: LoginRequest):
    """Authenticate user, return JWT token."""
    return login(req.email, req.password)


@app.get("/auth/me")
def auth_me(current_user: dict = Depends(get_current_user)):
    """Return the current user from the JWT. Used to verify token on page load."""
    return {"user": current_user}


# ── Repo analysis ─────────────────────────────────────────────────
class RepoRequest(BaseModel):
    url: str


@app.post("/analyze")
def analyze_repo(
    request: RepoRequest,
    current_user: dict = Depends(get_current_user),  
):
    try:
        files_dict = extract_python_files(request.url)
        if not files_dict:
            return {"status": "error", "message": "No Python files found."}
        predictions = predictor.predict(files_dict)
        return {
            "status": "success",
            "predictions": predictions,
            "raw_files": files_dict,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── LLM review  ────────────────────────────────────────────────────
class ReviewRequest(BaseModel):
    file_name: str
    code_snippet: str
    bug_probability: float = 50.0


@app.post("/review")
def review_file(
    request: ReviewRequest,
    current_user: dict = Depends(get_current_user),  
):
    try:
        result = run_code_review(
            file_name=request.file_name,
            code=request.code_snippet,
            bug_probability=request.bug_probability,
        )
        return {"status": "success", "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}
