"""
auth.py — JWT-based authentication for BugRadar AI
----------------------------------------------------
Uses:
  - bcrypt  : hash passwords before storing (never store plain text)
  - PyJWT   : create and verify JSON Web Tokens (stateless sessions)
  - json    : store users in a local users.json file (no DB needed)

How it works:
  1. Signup  → hash password → save to users.json → return JWT
  2. Login   → load user → verify bcrypt hash → return JWT
  3. Protected routes → read "Authorization: Bearer <token>" header
                      → decode JWT → get current user
"""

import os
import json
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi import HTTPException, Header
from typing import Optional

# ── Config ────────────────────────────────────────────────────────────────────
# Secret key signs JWTs. In production use a long random string from env vars.
SECRET_KEY  = os.getenv("JWT_SECRET_KEY", "bugradar-super-secret-change-in-production")
ALGORITHM   = "HS256"
TOKEN_HOURS = 24  # token stays valid for 24 hours

# ── Storage ───────────────────────────────────────────────────────────────────
# users.json lives next to auth.py (inside backend/)
_HERE       = Path(__file__).resolve().parent
USERS_FILE  = _HERE / "users.json"


def _load_users() -> dict:
    """Read users.json → dict of { email: {name, hashed_password} }"""
    if not USERS_FILE.exists():
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)


def _save_users(users: dict) -> None:
    """Write users dict back to users.json"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


# ── Password helpers ──────────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    """bcrypt hash a plain-text password. Returns a string."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Check plain password against stored bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# ── JWT helpers ───────────────────────────────────────────────────────────────
def create_token(email: str, name: str) -> str:
    """Create a signed JWT that contains the user's email and name."""
    payload = {
        "sub":  email,           # subject = who this token belongs to
        "name": name,
        "exp":  datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT. Raises HTTPException on failure."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")


# ── Auth actions ──────────────────────────────────────────────────────────────
def signup(email: str, name: str, password: str) -> dict:
    """
    Register a new user.
    Returns { token, user: {email, name} }
    Raises 400 if email already exists.
    """
    if not email or not name or not password:
        raise HTTPException(status_code=400, detail="All fields are required.")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    users = _load_users()
    if email in users:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    users[email] = {
        "name":            name,
        "hashed_password": hash_password(password),
        "created_at":      datetime.now(timezone.utc).isoformat(),
    }
    _save_users(users)

    token = create_token(email, name)
    return {"token": token, "user": {"email": email, "name": name}}


def login(email: str, password: str) -> dict:
    """
    Authenticate an existing user.
    Returns { token, user: {email, name} }
    Raises 401 on wrong credentials (deliberately vague for security).
    """
    users = _load_users()
    user  = users.get(email)

    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    token = create_token(email, user["name"])
    return {"token": token, "user": {"email": email, "name": user["name"]}}


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    FastAPI dependency — reads the Authorization header,
    verifies the JWT, and returns { email, name }.
    Use as:  current_user: dict = Depends(get_current_user)
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated.")
    token = authorization.split(" ", 1)[1]
    data  = decode_token(token)
    return {"email": data["sub"], "name": data["name"]}
