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
│   ├── main.py          # FastAPI routes + auth
│   ├── ml_model.py      # CodeBERT + PyTorch inference
│   ├── github_utils.py  # Git clone + file extraction
│   ├── llm_retriwer.py  # LangGraph 4-step agent
│   └── auth.py          # JWT signup/login
├── frontend/
│   └── react/
│       └── index.html   # Full React app (no build needed)
├── models/              # Trained weights (git-ignored)
└── requirements.txt
```