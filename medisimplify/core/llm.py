"""Thin wrapper around the Gemini API."""
import os
import re
import json
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
_client = None


def get_client():
    global _client
    if _client is None:
        key = os.getenv("GEMINI_API_KEY")
        if not key or key.startswith("PASTE_"):
            raise RuntimeError("GEMINI_API_KEY is missing. Put it in the .env file.")
        _client = genai.Client(api_key=key)
    return _client


def parse_json(text: str):
    """Parse JSON even if the model wrapped it in code fences or extra text."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def ask_gemini(prompt, system=None, json_mode=False, file_bytes=None,
               mime_type=None, retries=3, temperature=0.2):
    """Send a prompt (optionally with a file) to Gemini. Returns str or parsed JSON."""
    client = get_client()
    contents = []
    if file_bytes is not None:
        contents.append(types.Part.from_bytes(data=file_bytes, mime_type=mime_type))
    contents.append(prompt)

    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
        response_mime_type="application/json" if json_mode else None,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    last_error = None
    for attempt in range(retries):
        try:
            resp = client.models.generate_content(model=MODEL, contents=contents, config=config)
            text = resp.text or ""
            return parse_json(text) if json_mode else text
        except Exception as e:  # network, rate limit, bad JSON
            last_error = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Gemini request failed: {last_error}")
