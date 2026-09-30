# MediSimplify
Converts complex medical documents into plain-language explanations (English, Telugu, Hindi) with read-aloud
and grounded follow-up Q&A.

## Safety design
- Every item tagged "From your document" vs "General explanation"
- Prompts forbid diagnosis/treatment advice; dose/stop-medicine questions are refused and redirected to the doctor
- Hallucination check: extracted drugs, doses and lab values must appear in the source text
- Q&A answers only from retrieved document chunks (BM25) with a supporting quote; otherwise "not in your document"
- Persistent disclaimer banner + "Questions to ask your doctor"

## Run
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# put your key in .env
streamlit run app.py
```
