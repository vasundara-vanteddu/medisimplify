import os
import json
from dotenv import load_dotenv

load_dotenv()
from core.llm import ask_gemini, get_client
from core.simplifier import simplify
from core.validator import validate
from core.translator import translate_result
from core.qa import answer_question
from core.retriever import chunk_text
from google.genai.errors import APIError

def test():
    print("Testing basic ask_gemini...")
    try:
        ans = ask_gemini("Say hello")
        print("ask_gemini said:", ans)
    except Exception as e:
        print("ask_gemini failed:", e)
        print("Attempting to list models...")
        try:
            client = get_client()
            for m in client.models.list_models():
                print(m.name)
        except Exception as e2:
            print("Failed to list models:", e2)
        return

    print("\nReading sample...")
    with open("samples/sample_discharge_summary.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    print("\nSimplifying...")
    try:
        res = simplify(raw_text)
        print("Simplify success! Result keys:", res.keys())
    except Exception as e:
        print("Simplify failed:", e)
        return
        
    print("\nValidating...")
    try:
        val_res = validate(res, raw_text)
        print("Validation summary:", val_res.get("verification_summary"))
    except Exception as e:
        print("Validation failed:", e)
        return

    print("\nTranslating...")
    try:
        te = translate_result(val_res, "te")
        print("Telugu document_type:", te.get("document_type"))
        hi = translate_result(val_res, "hi")
        print("Hindi document_type:", hi.get("document_type"))
    except Exception as e:
        print("Translate failed:", e)

    print("\nQA Testing...")
    chunks = chunk_text(raw_text)
    
    q1 = "What is Clopidogrel for?"
    ans1 = answer_question(q1, chunks)
    print(f"Q: {q1}\nA:", ans1)
    
    q2 = "Can I double my dose?"
    ans2 = answer_question(q2, chunks)
    print(f"Q: {q2}\nA:", ans2)
    
    q3 = "What is my blood group?"
    ans3 = answer_question(q3, chunks)
    print(f"Q: {q3}\nA:", ans3)

if __name__ == "__main__":
    test()
