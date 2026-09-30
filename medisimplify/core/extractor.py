"""PDF / image / text  ->  plain text."""
import os

import fitz  # PyMuPDF

from core.llm import ask_gemini

OCR_PROMPT = ("Transcribe ALL text in this medical document exactly as written, preserving numbers, "
              "units, drug names and layout order. Do not interpret, summarise or correct anything.")

IMAGE_MIMES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        return file_bytes.decode("utf-8", errors="ignore")

    if ext == ".pdf":
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            text = "\n".join(page.get_text() for page in doc)
        if len(text.strip()) < 50:  # scanned PDF -> use Gemini OCR
            text = ask_gemini(OCR_PROMPT, file_bytes=file_bytes, mime_type="application/pdf")
        return text.strip()

    if ext in IMAGE_MIMES:
        return ask_gemini(OCR_PROMPT, file_bytes=file_bytes, mime_type=IMAGE_MIMES[ext]).strip()

    raise ValueError(f"Unsupported file type: {ext}")
