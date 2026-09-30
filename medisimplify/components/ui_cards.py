"""Render result sections with source badges + read-aloud text builders."""
import streamlit as st


def badge(tag: str) -> str:
    return "🟢 From your document" if tag == "from_document" else "🔵 General explanation"


def _unverified_note(item):
    if item.get("verified") is False:
        st.warning("⚠️ Could not verify this in the original text. Please check the original document.")


# ---------- text builders for read-aloud ----------
def summary_text(r):
    return r.get("summary", {}).get("text", "")


def meds_text(r):
    parts = []
    for m in r.get("medications", []):
        parts.append(f"{m.get('name','')}. {m.get('dose_as_written','')} {m.get('frequency_as_written','')}. "
                     f"{m.get('instructions_as_written','')} {m.get('purpose_general','')}")
    return "\n".join(parts)


def labs_text(r):
    return "\n".join(f"{l.get('test','')}: {l.get('value','')} {l.get('unit','')}. {l.get('explanation','')}"
                     for l in r.get("lab_results", []))


def glossary_text(r):
    return "\n".join(f"{g.get('term','')}: {g.get('meaning','')}" for g in r.get("glossary", []))


# ---------- renderers ----------
def render_summary(r):
    st.subheader("Summary")
    st.write(summary_text(r))
    st.caption(badge(r.get("summary", {}).get("source_tag", "from_document")))

    if r.get("diagnoses"):
        st.subheader("Diagnoses")
        for d in r["diagnoses"]:
            with st.container(border=True):
                st.markdown(f"**{d.get('term','')}**")
                st.write(d.get("explanation", ""))
                st.caption(badge(d.get("source_tag", "general_explanation")))

    if r.get("follow_up"):
        st.subheader("Follow-up instructions (as written in your document)")
        for f in r["follow_up"]:
            st.markdown(f"- {f}")

    if r.get("questions_for_doctor"):
        st.subheader("Questions you can ask your doctor")
        for q in r["questions_for_doctor"]:
            st.markdown(f"- {q}")


def render_meds(r):
    if not r.get("medications"):
        st.info("No medicines found in this document.")
        return
    for m in r["medications"]:
        with st.container(border=True):
            st.markdown(f"### 💊 {m.get('name','')}")
            cols = st.columns(2)
            cols[0].markdown(f"**Dose (as written):** {m.get('dose_as_written') or '—'}")
            cols[1].markdown(f"**How often (as written):** {m.get('frequency_as_written') or '—'}")
            if m.get("instructions_as_written"):
                st.markdown(f"**Instructions (as written):** {m['instructions_as_written']}")
            if m.get("purpose_general"):
                st.markdown(f"**What this medicine is generally for:** {m['purpose_general']}")
                st.caption("🔵 General explanation — not specific to you")
            st.caption(badge(m.get("source_tag", "from_document")))
            _unverified_note(m)


def render_labs(r):
    if not r.get("lab_results"):
        st.info("No lab results found in this document.")
        return
    for l in r["lab_results"]:
        with st.container(border=True):
            st.markdown(f"### 🧪 {l.get('test','')}")
            cols = st.columns(3)
            cols[0].markdown(f"**Value:** {l.get('value','')} {l.get('unit','')}")
            cols[1].markdown(f"**Range (as written):** {l.get('reference_range_as_written') or '—'}")
            cols[2].markdown(f"**Status (as written):** {l.get('status_as_written') or '—'}")
            st.write(l.get("explanation", ""))
            st.caption(badge(l.get("source_tag", "from_document")))
            _unverified_note(l)


def render_glossary(r):
    if not r.get("glossary"):
        st.info("No glossary terms.")
        return
    for g in r["glossary"]:
        st.markdown(f"**{g.get('term','')}** — {g.get('meaning','')}")
