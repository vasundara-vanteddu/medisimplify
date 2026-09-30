"""Disclaimers and blocked-intent detection."""
import re

DISCLAIMER = (
    "⚠️ **This tool explains your document in simple words. It is NOT medical advice.** "
    "It cannot diagnose, change treatment, or replace your doctor. "
    "Always confirm with your doctor or pharmacist."
)

REFUSALS = {
    "en": ("I can't advise on stopping, skipping or changing medicines, doses, or treatment. "
           "That is a decision for your doctor. Please ask your doctor or pharmacist."),
    "te": ("మందులను ఆపడం, మోతాదు మార్చడం లేదా చికిత్స నిర్ణయాల గురించి నేను సలహా ఇవ్వలేను. "
           "ఇది మీ డాక్టర్ నిర్ణయించాల్సిన విషయం. దయచేసి మీ డాక్టర్ లేదా ఫార్మసిస్ట్‌ను అడగండి."),
    "hi": ("मैं दवा बंद करने, छोड़ने या खुराक/इलाज बदलने के बारे में सलाह नहीं दे सकता। "
           "यह आपके डॉक्टर का निर्णय है। कृपया अपने डॉक्टर या फार्मासिस्ट से पूछें।"),
}

NOT_FOUND = {
    "en": "This isn't mentioned in your document. Please ask your doctor.",
    "te": "ఇది మీ డాక్యుమెంట్‌లో ప్రస్తావించబడలేదు. దయచేసి మీ డాక్టర్‌ను అడగండి.",
    "hi": "इसका उल्लेख आपके दस्तावेज़ में नहीं है। कृपया अपने डॉक्टर से पूछें।",
}

_ADVICE_PATTERNS = [
    r"\bstop (taking|the|my)\b", r"\bshould i (stop|skip|take|increase|decrease|double|reduce|quit)\b",
    r"\bcan i (stop|skip|double|increase|decrease|reduce|quit|take)\b",
    r"\b(double|increase|decrease|reduce|change|skip|miss) (the |my )?(dose|dosage|tablet|medicine|medication)\b",
    r"\bhow much (should|can) i take\b", r"\binstead of\b", r"\bwhat (medicine|drug|treatment) should i\b",
    r"\bdo i have (cancer|diabetes|a disease)\b", r"\bam i going to (die|be okay)\b",
    r"\bis it safe to\b", r"\bwhat is my prognosis\b",
]


def is_advice_request(question: str) -> bool:
    q = question.lower()
    return any(re.search(p, q) for p in _ADVICE_PATTERNS)
