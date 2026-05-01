import os
from typing import TypedDict, Literal
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph
from dotenv import load_dotenv

load_dotenv()


class ReviewerState(TypedDict):
    file_name: str
    code_snippet: str
    bug_probability: float
    bug_summary: str
    code_critique: str
    fixed_code: str
    test_suggestions: str
    final_report: str
    next_step: str


_llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-Coder-7B-Instruct",
    task="conversational",
    max_new_tokens=512,
)
chat_model = ChatHuggingFace(llm=_llm)


def _call(prompt: str) -> str:
    response = chat_model.invoke([HumanMessage(content=prompt)])
    if isinstance(response, AIMessage):
        return response.content.strip()
    return str(response).strip()


def node_hypothesize(state: ReviewerState) -> dict:
    prob = state["bug_probability"]
    severity = "critical" if prob >= 70 else "moderate" if prob >= 40 else "minor"
    prompt = f"""You are a senior Python engineer doing a code audit.

File: {state["file_name"]}
ML bug-probability score: {prob:.1f}% (severity: {severity})

First section of code:
```python
{state["code_snippet"][:1500]}
```

Based on the file name, the ML score, and the opening code:
1. What category of bugs is this file most likely to contain?
2. Why did the ML model likely flag this file at {prob:.1f}%?
3. What should a reviewer look for specifically?

Reply in 3 short bullet points. Be specific and direct."""
    return {"bug_summary": _call(prompt), "next_step": "critique"}


def node_critique(state: ReviewerState) -> dict:
    prompt = f"""You are a senior Python code reviewer. The previous analysis identified:

{state["bug_summary"]}

Now read the FULL code and find concrete problems:

File: {state["file_name"]}
```python
{state["code_snippet"]}
```

List up to 5 specific bugs. For each mention:
- Line number or function name
- What is wrong
- Why it's a problem

Format as a numbered list. Be precise and actionable."""
    return {"code_critique": _call(prompt), "next_step": "fix"}


def node_fix(state: ReviewerState) -> dict:
    prompt = f"""You are a Python expert. Issues found in {state["file_name"]}:

{state["code_critique"]}

Original code:
```python
{state["code_snippet"][:3000]}
```

Rewrite the code to fix the identified issues.
- Keep the same structure and logic
- Add proper error handling where missing
- Return ONLY the corrected Python code inside a ```python block."""
    fixed = _call(prompt)
    if "```python" in fixed:
        fixed = fixed.split("```python", 1)[1].split("```")[0].strip()
    elif "```" in fixed:
        fixed = fixed.split("```", 1)[1].split("```")[0].strip()
    return {"fixed_code": fixed, "next_step": "tests"}


def node_tests(state: ReviewerState) -> dict:
    prompt = f"""You are a Python QA engineer. Bugs found in {state["file_name"]}:

{state["code_critique"]}

Suggest 3 pytest test cases that catch these bugs. Write actual function signatures and assert statements."""
    return {"test_suggestions": _call(prompt), "next_step": "report"}


def node_report(state: ReviewerState) -> dict:
    prob = state["bug_probability"]
    badge = "HIGH RISK" if prob >= 60 else "MEDIUM RISK" if prob >= 30 else "LOW RISK"
    report = f"""## {badge} — `{state["file_name"]}`
**ML Bug Probability: {prob:.1f}%**

---

### Bug Hypothesis
{state["bug_summary"]}

---

### Specific Issues Found
{state["code_critique"]}

---

### Fixed Code
```python
{state["fixed_code"]}
```

---

### Suggested Unit Tests
{state["test_suggestions"]}
"""
    return {"final_report": report, "next_step": "done"}


def router(state: ReviewerState) -> Literal["critique", "fix", "tests", "report", "__end__"]:
    mapping = {"critique": "critique", "fix": "fix", "tests": "tests", "report": "report"}
    return mapping.get(state.get("next_step", "done"), "__end__")


workflow = StateGraph(ReviewerState)
workflow.add_node("hypothesize", node_hypothesize)
workflow.add_node("critique",    node_critique)
workflow.add_node("fix",         node_fix)
workflow.add_node("tests",       node_tests)
workflow.add_node("report",      node_report)

workflow.set_entry_point("hypothesize")
workflow.add_conditional_edges("hypothesize", router)
workflow.add_conditional_edges("critique",    router)
workflow.add_conditional_edges("fix",         router)
workflow.add_conditional_edges("tests",       router)
workflow.add_conditional_edges("report",      router)

code_reviewer_app = workflow.compile()


def run_code_review(file_name: str, code: str, bug_probability: float = 50.0) -> dict:
    if not os.getenv("HUGGINGFACEHUB_API_TOKEN"):
        raise ValueError("HUGGINGFACEHUB_API_TOKEN is not set in environment.")

    initial_state: ReviewerState = {
        "file_name":       file_name,
        "code_snippet":    code,
        "bug_probability": bug_probability,
        "bug_summary":     "",
        "code_critique":   "",
        "fixed_code":      "",
        "test_suggestions": "",
        "final_report":    "",
        "next_step":       "hypothesize",   # ← was "critique" (bug: skipped first node)
    }

    final_state = code_reviewer_app.invoke(initial_state)
    return {
        "bug_summary":      final_state["bug_summary"],
        "code_critique":    final_state["code_critique"],
        "fixed_code":       final_state["fixed_code"],
        "test_suggestions": final_state["test_suggestions"],
        "final_report":     final_state["final_report"],
    }
