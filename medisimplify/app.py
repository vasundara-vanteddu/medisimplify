import os
import streamlit as st

from core.extractor import extract_text
from core.simplifier import simplify
from core.validator import validate
from core.retriever import chunk_text
from core.qa import answer_question
from core.translator import translate_result
from core.safety import DISCLAIMER
from components import ui_cards as ui
from components.tts import read_aloud

st.set_page_config(page_title="MediSimplify", page_icon="🩺", layout="wide")

LANGS = {"English": ("en", "en-IN"), "తెలుగు (Telugu)": ("te", "te-IN"), "हिन्दी (Hindi)": ("hi", "hi-IN")}
SAMPLE_PATH = os.path.join("samples", "sample_discharge_summary.txt")

for key, default in {"raw_text": "", "result_en": None, "translations": {}, "chunks": [], "chat": []}.items():
    st.session_state.setdefault(key, default)


def process(raw_text: str):
    result = simplify(raw_text)
    result = validate(result, raw_text)
    st.session_state.update(raw_text=raw_text, result_en=result, translations={},
                            chunks=chunk_text(raw_text), chat=[])


# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("🩺 MediSimplify")
    st.caption("Medical documents in plain language")
    uploaded = st.file_uploader("Upload document", type=["pdf", "png", "jpg", "jpeg", "txt"])
    pasted = st.text_area("...or paste text", height=120)
    col1, col2 = st.sidebar.columns(2)
    go = col1.button("Simplify", type="primary", use_container_width=True)
    sample = col2.button("Try sample", use_container_width=True)
    lang_label = st.selectbox("Language", list(LANGS.keys()))
    st.divider()
    st.caption("Use sample or anonymized documents only. Free API tiers may retain data.")

lang, tts_lang = LANGS[lang_label]

# ---------------- Header ----------------
st.title("MediSimplify")
st.warning(DISCLAIMER)

# ---------------- Processing ----------------
if go or sample:
    try:
        with st.spinner("Reading and simplifying your document..."):
            if sample:
                raw = open(SAMPLE_PATH, encoding="utf-8").read()
            elif uploaded:
                raw = extract_text(uploaded.getvalue(), uploaded.name)
            elif pasted.strip():
                raw = pasted
            else:
                raw = ""
            if not raw.strip():
                st.error("Please upload a file, paste text, or try the sample.")
            else:
                process(raw)
    except Exception as e:
        st.error(f"Something went wrong: {e}")

result_en = st.session_state.result_en
if not result_en:
    st.info("👈 Upload a discharge summary, prescription or lab report — or click **Try sample**.")
    st.stop()

# ---------------- Language handling ----------------
if lang == "en":
    result = result_en
else:
    if lang not in st.session_state.translations:
        try:
            with st.spinner("Translating..."):
                st.session_state.translations[lang] = translate_result(result_en, lang)
        except Exception as e:
            st.error(f"Translation failed: {e}")
    result = st.session_state.translations.get(lang, result_en)

vs = result_en.get("verification_summary", {})
if vs.get("flagged"):
    st.error(f"⚠️ {vs['flagged']} of {vs['checked']} extracted items could not be verified in the original text. "
             "Check the flagged items against your document.")
elif vs.get("checked"):
    st.success(f"✅ All {vs['checked']} medicines/lab values were found in your original document.")

# ---------------- Tabs ----------------
t1, t2, t3, t4, t5 = st.tabs(["📄 Summary", "💊 Medicines", "🧪 Lab Results", "📖 Glossary", "💬 Ask Questions"])

with t1:
    read_aloud(ui.summary_text(result), tts_lang)
    ui.render_summary(result)
with t2:
    read_aloud(ui.meds_text(result), tts_lang)
    ui.render_meds(result)
with t3:
    read_aloud(ui.labs_text(result), tts_lang)
    ui.render_labs(result)
with t4:
    read_aloud(ui.glossary_text(result), tts_lang)
    ui.render_glossary(result)

with t5:
    st.caption("Answers come only from your uploaded document. Treatment and dose decisions are for your doctor.")
    for turn in st.session_state.chat:
        with st.chat_message("user"):
            st.write(turn["q"])
        with st.chat_message("assistant"):
            st.write(turn["a"]["answer"])
            if turn["a"]["quote"]:
                st.caption(f"📎 From your document: “{turn['a']['quote']}”")
            if turn["a"]["type"] == "refusal":
                st.caption("🚫 Medical-advice question — please ask your doctor.")

    with st.form("qa_form", clear_on_submit=True):
        q = st.text_input("Ask a question about your document", placeholder="e.g. What is Clopidogrel for?")
        asked = st.form_submit_button("Ask")
    if asked and q.strip():
        try:
            with st.spinner("Searching your document..."):
                ans = answer_question(q.strip(), st.session_state.chunks, lang)
            st.session_state.chat.append({"q": q.strip(), "a": ans})
            st.rerun()
        except Exception as e:
            st.error(f"Could not answer: {e}")
