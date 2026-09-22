"""
ingest.py — Chunk source documents and build the Chroma vector store.

Run this once (and again any time you add/update files in sources/).

Embedding note: this uses a TF-IDF vectorizer (scikit-learn) computed locally,
not a downloaded neural embedding model. That was a deliberate swap: Chroma's
default ONNX MiniLM embedding function needs to download its model weights from
a host that wasn't reachable in the sandbox this was built in. On your own
machine (full internet access), swap this for real sentence-transformer or API
embeddings for better semantic quality — see the "Upgrading the embeddings"
note at the bottom of this file. TF-IDF still gives correct keyword-driven
retrieval for a domain like this one, where questions use fairly specific,
consistent terminology (STEM OPT, 90-day rule, I-983, etc).
"""

import os
import glob
import pickle
import chromadb
from sklearn.feature_extraction.text import TfidfVectorizer

SOURCES_DIR = os.path.join(os.path.dirname(__file__), "sources")
DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "tfidf_vectorizer.pkl")
COLLECTION_NAME = "opt_compliance"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """Paragraph-aware sliding-window chunker — splits on paragraph boundaries so
    we don't cut an eligibility requirement or a deadline rule in half mid-sentence."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 1 <= chunk_size:
            current = (current + "\n\n" + para).strip()
        else:
            if current:
                chunks.append(current)
            overlap_text = current[-overlap:] if current else ""
            current = (overlap_text + "\n\n" + para).strip()
    if current:
        chunks.append(current)
    return chunks


def main():
    source_files = sorted(glob.glob(os.path.join(SOURCES_DIR, "*.txt")))
    if not source_files:
        print(f"No .txt files found in {SOURCES_DIR}. Add source documents first.")
        return

    all_ids, all_docs, all_metas = [], [], []

    for filepath in source_files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        lines = text.split("\n", 1)
        source_label = lines[0].replace("Source:", "").strip() if lines[0].startswith("Source:") else filename
        body = lines[1] if len(lines) > 1 else text

        for i, chunk in enumerate(chunk_text(body)):
            all_ids.append(f"{filename}::chunk{i}")
            all_docs.append(chunk)
            all_metas.append({"source_file": filename, "source_label": source_label})

    # Fit TF-IDF over all chunks, then persist the fitted vectorizer so queries
    # at inference time can be transformed into the same vector space.
    vectorizer = TfidfVectorizer(stop_words="english", max_features=4096)
    tfidf_matrix = vectorizer.fit_transform(all_docs)
    embeddings = tfidf_matrix.toarray().tolist()

    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    client = chromadb.PersistentClient(path=DB_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    # embedding_function=None: we supply embeddings ourselves at add() and query() time
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=None)
    collection.add(ids=all_ids, documents=all_docs, metadatas=all_metas, embeddings=embeddings)

    print(f"Ingested {len(source_files)} source files -> {len(all_ids)} chunks into '{COLLECTION_NAME}'")
    print(f"Vector store persisted at: {DB_DIR}")
    print(f"TF-IDF vectorizer saved at: {VECTORIZER_PATH}")


if __name__ == "__main__":
    main()

# --- Upgrading the embeddings (do this on your own machine, not required for the demo) ---
# Replace the TfidfVectorizer block above with, e.g.:
#   from sentence_transformers import SentenceTransformer
#   model = SentenceTransformer("all-MiniLM-L6-v2")
#   embeddings = model.encode(all_docs).tolist()
# and apply the same swap to rag_chain.py's query-time embedding step.
