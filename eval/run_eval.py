"""
run_eval.py — Runs every question in test_questions.md against retrieve() and
checks whether the top-retrieved chunk came from the expected source file.
This measures retrieval accuracy, which is the RAG layer's actual job — the
generation layer (Claude) is graded separately/manually since it needs a
human or LLM judge to assess answer quality, not just source match.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag_chain import retrieve  # noqa: E402

QUESTIONS = [
    ("How many days can I be unemployed on regular post-completion OPT?", "02_90day_unemployment_rule"),
    ("Does the 90-day unemployment rule apply during pre-completion OPT?", "02_90day_unemployment_rule"),
    ("Do I need a job offer to apply for standard OPT?", "01_opt_overview"),
    ("How many months of STEM OPT extension can I get?", "03_stem_opt_extension"),
    ("What are the eligibility requirements for the STEM OPT extension?", "03_stem_opt_extension"),
    ("Can I do unpaid volunteer work while on the STEM OPT extension?", "03_stem_opt_extension"),
    ("How many days of unemployment are allowed during the STEM OPT extension?", "03_stem_opt_extension"),
    ("Does my employer need to be enrolled in E-Verify for the STEM extension?", "03_stem_opt_extension"),
    ("When do I need to submit my STEM OPT 6-month report?", "03_stem_opt_extension"),
    ("What form do I need for the STEM OPT training plan?", "03_stem_opt_extension"),
    ("How far in advance can I apply for the STEM OPT extension?", "03_stem_opt_extension"),
    ("What's the difference between CPT and OPT?", "04_cpt"),
    ("Does CPT require a separate EAD card?", "04_cpt"),
    ("If I use full-time CPT for 12 months, does that affect my OPT eligibility?", "04_cpt"),
    ("What is the window for applying for post-completion OPT relative to my graduation date?", "01_opt_overview"),
    ("Can I start working before I physically have my EAD card?", "01_opt_overview"),
    ("Within how many days of the DSO's OPT recommendation must USCIS receive my application?", "01_opt_overview"),
    ("What's the maximum total time (standard + STEM) I can be on OPT?", "03_stem_opt_extension"),
    ("What happens if I change employers during the STEM OPT extension?", "03_stem_opt_extension"),
    ("What is Curricular Practical Training used for?", "04_cpt"),
]


def main():
    correct = 0
    print(f"{'#':<3} {'Result':<8} {'Top Source':<45} Question")
    print("-" * 110)
    for i, (question, expected_file) in enumerate(QUESTIONS, 1):
        hits = retrieve(question, k=1)
        top_source_file = None
        if hits:
            # source_label doesn't include filename directly, so re-retrieve with metadata
            pass
        # Re-run with access to source_file metadata directly
        from rag_chain import _load
        vectorizer, collection = _load()
        query_vec = vectorizer.transform([question]).toarray().tolist()
        results = collection.query(query_embeddings=query_vec, n_results=1)
        top_file = results["metadatas"][0][0]["source_file"] if results["metadatas"][0] else "NONE"

        is_correct = top_file.startswith(expected_file)
        correct += is_correct
        status = "PASS" if is_correct else "FAIL"
        print(f"{i:<3} {status:<8} {top_file:<45} {question[:60]}")

    print("-" * 110)
    print(f"\nRetrieval accuracy: {correct}/{len(QUESTIONS)} ({100*correct/len(QUESTIONS):.0f}%)")


if __name__ == "__main__":
    main()
