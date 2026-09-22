"""
app.py — Streamlit frontend for the OPT/F-1 Compliance Copilot.

Run with: streamlit run app.py
Requires ANTHROPIC_API_KEY set in your environment for real generated answers
(falls back to showing raw retrieved context otherwise — see rag_chain.py).
"""

import streamlit as st
from rag_chain import answer, DISCLAIMER
from router import route, handle_deadline_query

st.set_page_config(page_title="OPT/F-1 Compliance Copilot", page_icon="🎓")

st.title("🎓 OPT/F-1 Compliance Copilot")
st.caption(
    "Answers CPT/OPT/STEM-extension questions from official USCIS/SEVP/ISSS source "
    "documents, with citations. Built because I lived this exact problem."
)
st.warning(DISCLAIMER, icon="⚠️")

with st.sidebar:
    st.subheader("Your dates (for deadline tracking)")
    opt_start = st.date_input("OPT start date (EAD start)", value=None)
    stem_start = st.date_input("STEM OPT extension start date (if applicable)", value=None)
    st.caption(
        "Ask a deadline question like \"when is my STEM OPT report due\" to use these."
    )

if "history" not in st.session_state:
    st.session_state.history = []

for role, text in st.session_state.history:
    with st.chat_message(role):
        st.markdown(text)

user_input = st.chat_input("Ask a question, e.g. 'Can I do unpaid work on my STEM extension?'")

if user_input:
    st.session_state.history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    intent = route(user_input)

    if intent == "deadline":
        user_dates = {
            "opt_start": opt_start.isoformat() if opt_start else None,
            "stem_start": stem_start.isoformat() if stem_start else None,
        }
        response_text = handle_deadline_query(user_input, user_dates)
    else:
        result = answer(user_input)
        response_text = result["answer"]
        if result["sources"]:
            response_text += "\n\n**Sources:** " + "; ".join(result["sources"])

    st.session_state.history.append(("assistant", response_text))
    with st.chat_message("assistant"):
        st.markdown(response_text)
