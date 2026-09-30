"""raw text -> structured, simplified JSON."""
from core.llm import ask_gemini
from core.prompts import SIMPLIFY_SYSTEM, SIMPLIFY_PROMPT

MAX_CHARS = 30000
LIST_KEYS = ["diagnoses", "medications", "lab_results", "follow_up", "glossary", "questions_for_doctor"]


def simplify(raw_text: str) -> dict:
    prompt = SIMPLIFY_PROMPT.replace("<<DOC>>", raw_text[:MAX_CHARS])
    result = ask_gemini(prompt, system=SIMPLIFY_SYSTEM, json_mode=True)
    if not isinstance(result, dict):
        raise ValueError("Model returned unexpected format.")
    result.setdefault("document_type", "other")
    result.setdefault("summary", {"text": "", "source_tag": "from_document"})
    if isinstance(result["summary"], str):
        result["summary"] = {"text": result["summary"], "source_tag": "from_document"}
    for k in LIST_KEYS:
        result.setdefault(k, [])
    return result
