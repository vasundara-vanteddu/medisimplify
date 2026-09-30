"""Grounded follow-up Q&A with refusal logic."""
from core.llm import ask_gemini
from core.prompts import QA_SYSTEM, QA_PROMPT
from core.retriever import top_chunks
from core.safety import is_advice_request, REFUSALS, NOT_FOUND

LANG_NAMES = {"en": "English", "te": "Telugu", "hi": "Hindi"}


def answer_question(question: str, chunks, lang: str = "en") -> dict:
    if is_advice_request(question):
        return {"answer": REFUSALS[lang], "quote": "", "type": "refusal"}

    context = "\n---\n".join(top_chunks(question, chunks))
    prompt = (QA_PROMPT.replace("<<CONTEXT>>", context)
              .replace("<<QUESTION>>", question)
              .replace("<<LANGUAGE>>", LANG_NAMES[lang]))
    res = ask_gemini(prompt, system=QA_SYSTEM, json_mode=True)

    if not res.get("grounded") or not res.get("answer"):
        return {"answer": NOT_FOUND[lang], "quote": "", "type": "not_found"}
    return {"answer": res["answer"], "quote": res.get("quote", ""), "type": "answer"}
