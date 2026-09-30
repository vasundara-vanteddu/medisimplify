"""Translate the simplified result into Telugu / Hindi."""
import json

from core.llm import ask_gemini
from core.prompts import TRANSLATE_SYSTEM, TRANSLATE_PROMPT

LANG_NAMES = {"te": "Telugu", "hi": "Hindi"}
PRESERVE = ("source_tag", "verified")


def translate_result(result: dict, lang: str) -> dict:
    prompt = (TRANSLATE_PROMPT.replace("<<LANGUAGE>>", LANG_NAMES[lang])
              .replace("<<JSON>>", json.dumps(result, ensure_ascii=False)))
    out = ask_gemini(prompt, system=TRANSLATE_SYSTEM, json_mode=True)

    # Restore tags/flags from the English original so they can never be altered.
    for key, orig_val in result.items():
        if isinstance(orig_val, list) and isinstance(out.get(key), list) and len(out[key]) == len(orig_val):
            for o, t in zip(orig_val, out[key]):
                if isinstance(o, dict) and isinstance(t, dict):
                    for p in PRESERVE:
                        if p in o:
                            t[p] = o[p]
        elif isinstance(orig_val, dict) and isinstance(out.get(key), dict):
            for p in PRESERVE:
                if p in orig_val:
                    out[key][p] = orig_val[p]
    out["verification_summary"] = result.get("verification_summary", {})
    out["document_type"] = result.get("document_type", "other")
    return out
