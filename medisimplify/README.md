# MediSimplify
Converts complex medical documents into plain-language explanations (English, Telugu, Hindi) with read-aloud
and grounded follow-up Q&A.

## Safety design
- Every item tagged "From your document" vs "General explanation"
- Prompts forbid diagnosis/treatment advice; dose/stop-medicine questions are refused and redirected to the doctor
- Hallucination check: extracted drugs, doses and lab values must appear in the source text
- Q&A answers only from retrieved document chunks (BM25) with a supporting quote; otherwise "not in your document"
- Persistent disclaimer banner + "Questions to ask your doctor"

## Run locally
1. Clone the repository: `git clone <repo_url>`
2. Navigate to the project directory: `cd medisimplify`
3. Create a virtual environment: `python -m venv .venv`
4. Activate the virtual environment: 
   - Windows: `.\.venv\Scripts\Activate.ps1` or `.\.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`
5. Install requirements: `pip install -r requirements.txt`
6. Copy `.env.example` to `.env` and add your real API key.
7. Run the app: `streamlit run app.py`
