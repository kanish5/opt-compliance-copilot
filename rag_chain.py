"""
rag_chain.py — Retrieval + generation for the OPT Compliance Copilot.

retrieve(query) is pure retrieval, no API key needed — usable for testing/eval.
answer(query) adds Claude generation on top and requires ANTHROPIC_API_KEY to be set.
"""

import os
import pickle
import chromadb

DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "tfidf_vectorizer.pkl")
COLLECTION_NAME = "opt_compliance"

DISCLAIMER = (
    "This is not legal advice. Confirm anything status-critical with your "
    "school's international student office (ISSS/DSO) or an immigration attorney "
    "before acting on it."
)

# Below this similarity score, we don't trust the retrieval enough to answer —
# refusing beats guessing here, given the stakes.
MIN_CONFIDENCE = 0.08


def _load():
    with open(VECTORIZER_PATH, "rb") as f:
        vectorizer = pickle.load(f)
    client = chromadb.PersistentClient(path=DB_DIR)
    collection = client.get_collection(name=COLLECTION_NAME, embedding_function=None)
    return vectorizer, collection


def retrieve(query: str, k: int = 4):
    """Returns a list of {text, source, score} dicts, best match first."""
    vectorizer, collection = _load()
    query_vec = vectorizer.transform([query]).toarray().tolist()
    results = collection.query(query_embeddings=query_vec, n_results=k)

    hits = []
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]  # Chroma returns distance; lower = closer

    for doc, meta, dist in zip(docs, metas, distances):
        similarity = 1.0 / (1.0 + dist)  # convert distance to a rough 0-1 similarity score
        hits.append({"text": doc, "source": meta["source_label"], "score": similarity})
    return hits


def answer(query: str, k: int = 4, model: str = "claude-sonnet-4-6"):
    """Retrieve + generate. Requires ANTHROPIC_API_KEY in the environment."""
    hits = retrieve(query, k=k)

    if not hits or hits[0]["score"] < MIN_CONFIDENCE:
        return {
            "answer": (
                "I don't have a confident answer to that from my source documents. "
                f"{DISCLAIMER} Please check directly with your ISSS office."
            ),
            "sources": [],
            "hits": hits,
        }

    context = "\n\n---\n\n".join(f"[Source: {h['source']}]\n{h['text']}" for h in hits)

    system_prompt = (
        "You are an F-1/OPT compliance assistant. Answer the student's question "
        "using ONLY the context provided below. If the context doesn't fully answer "
        "the question, say what you don't know rather than guessing. Always cite "
        f"which source(s) your answer draws from. End every answer with this exact "
        f"disclaimer on its own line: \"{DISCLAIMER}\"\n\n"
        f"Context:\n{context}"
    )

    try:
        import anthropic
        client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
        response = client.messages.create(
            model=model,
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": query}],
        )
        answer_text = response.content[0].text
    except Exception as e:
        # No API key set, or the call failed — fall back to showing the raw
        # retrieved context so the pipeline is still demonstrable without a key.
        answer_text = (
            "[No ANTHROPIC_API_KEY set — showing raw retrieved context instead of "
            f"a generated answer. Error: {e}]\n\n" + context + f"\n\n{DISCLAIMER}"
        )

    return {
        "answer": answer_text,
        "sources": sorted(set(h["source"] for h in hits)),
        "hits": hits,
    }


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "How many days can I be unemployed on OPT?"
    result = answer(q)
    print(f"Q: {q}\n")
    print(f"A: {result['answer']}\n")
    print(f"Sources: {result['sources']}")
