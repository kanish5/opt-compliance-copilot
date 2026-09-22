# OPT/F-1 Compliance Copilot

I'm an international student on the OPT-to-STEM-extension track myself, and the honest problem
is that the rules that decide whether you keep your legal status in the US live scattered across
USCIS pages, SEVP policy PDFs, and a dozen different university ISSS FAQ pages — and getting one
of them wrong (the 90-day unemployment count, a missed STEM OPT report) has real consequences,
not just an inconvenience. This is a RAG agent that answers those questions from official source
documents with citations, plus an automated reminder flow for the actual deadlines, so the answer
isn't just "read the 40-page policy PDF yourself."

**This is not legal advice.** Every answer this tool gives is meant to be a starting point,
not a final word — always confirm anything status-critical with your school's international
office or an immigration attorney.

## What it does

- Answers CPT/OPT/STEM-extension questions (eligibility, deadlines, reporting requirements,
  the 90-day and 150-day unemployment rules) by retrieving from official source documents and
  generating a cited answer via Claude.
- Tracks your personal OPT/STEM OPT dates and computes the actual deadlines that apply to you.
- Sends automated reminders before the deadlines that matter (unemployment ceiling approaching,
  STEM OPT 6/12/18/24-month reports coming due) via a scheduled n8n workflow.

## Architecture

```
sources/*.txt (USCIS/SEVP/ISSS content)
   -> ingest.py: paragraph-aware chunking + TF-IDF vectorization
   -> Chroma (local, persisted vector store)
   -> rag_chain.py: retrieval (top-k) + Claude generation with injected disclaimer
   -> router.py: routes "question" vs "deadline" intents
   -> app.py: Streamlit chat frontend
   -> automation/deadline_reminder_flow.json: n8n scheduled flow for proactive reminders
```

### A note on the embeddings

The retrieval layer uses TF-IDF vectors (scikit-learn), not a downloaded neural embedding
model. That was a deliberate choice made while building this in a sandboxed dev environment
without open internet access to model-hosting sites — on a normal machine, swap in real
sentence-transformer or API embeddings for better semantic (not just keyword) matching; see
the comment block at the bottom of `ingest.py` for the exact swap. TF-IDF still performs well
here because OPT/STEM compliance questions use fairly specific, consistent terminology.

## Results

Retrieval accuracy on a 20-question self-written eval set (`eval/test_questions.md`,
run via `eval/run_eval.py`): **19/20 (95%)** — the pipeline correctly retrieves the source
document that contains the answer for the corresponding question.

## Running it

```bash
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install chromadb scikit-learn anthropic streamlit

python ingest.py                    # build the vector store from sources/
python eval/run_eval.py             # check retrieval accuracy
export ANTHROPIC_API_KEY=sk-...     # required for generated (not just retrieved) answers
streamlit run app.py
```

For the deadline automation: import `automation/deadline_reminder_flow.json` into n8n,
set the `OPT_START_DATE`, `STEM_START_DATE`, `REMINDER_FROM_EMAIL`, and `REMINDER_TO_EMAIL`
environment variables (or hardcode them for a personal instance), and configure SMTP
credentials in n8n.

## Repo structure

```
opt-copilot/
  sources/                       # official OPT/CPT/STEM source documents
  ingest.py                      # chunk + vectorize + store
  rag_chain.py                   # retrieve + generate
  router.py                      # intent routing + deadline computation
  app.py                         # Streamlit frontend
  automation/
    deadline_reminder_flow.json  # n8n scheduled reminder workflow
  eval/
    test_questions.md            # 20-question eval set + 2 out-of-scope control questions
    run_eval.py                  # retrieval accuracy checker
```

## What's next (honest scope note)

This is a deliberately narrow v1: F-1/OPT/CPT/STEM only, no other visa categories, no
multi-user accounts, no HR-facing side. Real next steps if this grows: add international
travel guidance while on STEM OPT (currently an intentional gap, see eval question #22),
swap TF-IDF for real embeddings, and add a proper employment-gap tracker instead of the
current simplified unemployment-day estimate.
