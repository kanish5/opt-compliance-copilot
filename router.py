"""
router.py — Routes a user message to either the RAG Q&A pipeline or the
deadline-tracking lookup. Deliberately simple (keyword-based) rather than a
full agent framework — this is a 2-3 week MVP, not a production system.
"""

import re

DEADLINE_KEYWORDS = [
    "when is my", "how many days until", "deadline", "due date",
    "days left", "when do i need to", "reminder",
]


def route(message: str) -> str:
    """Returns 'deadline' or 'qa'."""
    lowered = message.lower()
    if any(kw in lowered for kw in DEADLINE_KEYWORDS):
        return "deadline"
    return "qa"


def handle_deadline_query(message: str, user_dates: dict) -> str:
    """
    user_dates example:
      {"opt_start": "2026-12-14", "stem_start": None}
    Computes the key dates a student actually needs to track. This is
    structured lookup, not RAG — the rules are fixed, the dates are the
    student's own data.
    """
    from datetime import date, datetime, timedelta

    if not user_dates.get("opt_start"):
        return "I don't have your OPT start date on file yet. Please enter it first."

    opt_start = datetime.strptime(user_dates["opt_start"], "%Y-%m-%d").date()
    today = date.today()
    days_elapsed = (today - opt_start).days

    lines = [f"Your OPT start date: {opt_start.isoformat()}"]
    lines.append(f"Days since OPT start: {days_elapsed}")
    lines.append(f"Unemployment days used (if any gaps): track manually — this MVP "
                  f"doesn't yet ingest actual employment gap dates, see README.")

    unemployment_limit_date = opt_start + timedelta(days=90)
    lines.append(
        f"Hard 90-day unemployment ceiling (cumulative, if unemployed the whole time): "
        f"{unemployment_limit_date.isoformat()}"
    )

    if user_dates.get("stem_start"):
        stem_start = datetime.strptime(user_dates["stem_start"], "%Y-%m-%d").date()
        for months, label in [(6, "6-month report"), (12, "12-month report + evaluation"),
                               (18, "18-month report"), (24, "24-month report + final evaluation")]:
            due = stem_start + timedelta(days=30 * months)
            lines.append(f"STEM OPT {label} due around: {due.isoformat()}")

    return "\n".join(lines)
