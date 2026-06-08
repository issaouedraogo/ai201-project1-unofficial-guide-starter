"""
Milestone 4: Embedding and retrieval.

Loads chunks from documents/all_chunks.json, embeds each one with
all-MiniLM-L6-v2 via SentenceTransformers, and stores them in a
persistent ChromaDB collection with source metadata.

Also exposes a retrieve() function used by Milestone 5.

Run once to build the index:
    pip install -r requirements.txt
    python embed.py

Then import retrieve() from other scripts:
    from embed import retrieve
"""

import json
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = Path("documents/all_chunks.json")
CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "cs_guides"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 5

# ---------------------------------------------------------------------------
# Setup: model + ChromaDB client
# ---------------------------------------------------------------------------

# Load the embedding model once at import time so retrieve() is fast
_model = SentenceTransformer(EMBED_MODEL)

# Persistent client — saves the index to disk so you don't re-embed every run
_client = chromadb.PersistentClient(path=str(CHROMA_DIR))


def _get_collection(reset: bool = False) -> chromadb.Collection:
    """
    Returns the ChromaDB collection, creating it if it doesn't exist.
    Pass reset=True to wipe and rebuild from scratch.

    ChromaDB stores vectors alongside metadata dicts. Each document
    needs a unique string id — we use its index in the chunk list.
    """
    if reset:
        try:
            _client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
    return _client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},  # cosine similarity for semantic search
    )


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def build_index() -> None:
    """
    Embeds all chunks from all_chunks.json and upserts them into ChromaDB.

    ChromaDB's add() call takes four parallel lists:
      - ids        : unique string identifiers (required)
      - documents  : the raw text of each chunk (stored as-is for retrieval)
      - embeddings : the float vectors we computed with SentenceTransformer
      - metadatas  : dicts of any extra fields you want to filter or display

    We upsert in batches of 100 to avoid sending one giant HTTP-like call.
    """
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"{CHUNKS_FILE} not found — run ingest.py first."
        )

    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    collection = _get_collection(reset=True)

    ids = [str(i) for i in range(len(chunks))]

    # Track position within each source so we can reconstruct context order later
    source_counters: dict[str, int] = {}
    metadatas = []
    for c in chunks:
        src = c["source"]
        pos = source_counters.get(src, 0)
        source_counters[src] = pos + 1
        metadatas.append({"source": src, "chunk_index": pos})

    # Prepend a human-readable source label to each chunk before embedding.
    # The boilerplate filter strips page titles (e.g. "COP 3502C UCF Reviews"),
    # so without this the course name never appears in the chunk text and
    # retrieval can't distinguish COP 3502C chunks from COP 3503C chunks.
    source_labels = {
        "reviews_cop3502c":             "COP 3502C (CS I, UCF)",
        "reviews_cop3503c":             "COP 3503C (CS II, UCF)",
        "reviews_csc241":               "CSC 241 (Intro CS I, DePaul)",
        "reviews_prof_kapp_nyu":        "Professor Craig Kapp (NYU)",
        "reviews_prof_decker_delaware": "Professor Keith Decker (University of Delaware)",
        "reviews_prof_mazidi_utdallas":  "Professor Karen Mazidi (UT Dallas)",
        "reddit_1_cs_courses_order":    "Reddit: recommended CS courses and learning order",
        "reddit_2_cs_foundation":       "Reddit: building a strong CS foundation",
        "reddit_3_data_structures":     "Reddit: advice for CS students preparing for Data Structures",
        "reddit_4_intro_cs_design":     "Reddit: design of an ideal intro CS course",
    }
    texts = []
    for c in chunks:
        label = source_labels.get(c["source"], c["source"])
        texts.append(f"[Source: {label}]\n{c['text']}")

    print(f"Embedding with {EMBED_MODEL} ...")
    embeddings = _model.encode(texts, show_progress_bar=True).tolist()

    # Upsert in batches — ChromaDB handles large adds fine, but batching
    # keeps memory usage predictable for larger corpora
    batch_size = 100
    for start in range(0, len(chunks), batch_size):
        end = start + batch_size
        collection.upsert(
            ids=ids[start:end],
            documents=texts[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end],
        )

    print(f"Indexed {len(chunks)} chunks into collection '{COLLECTION_NAME}'")
    print(f"Index saved to {CHROMA_DIR}/")


# ---------------------------------------------------------------------------
# Retrieval
# ---------------------------------------------------------------------------

def retrieve(query: str, top_k: int = TOP_K) -> list[dict]:
    """
    Embeds the query and returns the top_k most semantically similar chunks.

    ChromaDB's query() returns a dict of parallel lists (ids, documents,
    distances, metadatas). We zip them into a list of dicts so callers
    can iterate naturally.

    Each returned dict has:
      - text     : the chunk text
      - source   : which source document it came from
      - distance : cosine distance (lower = more similar; range 0–2)
    """
    collection = _get_collection()

    if collection.count() == 0:
        raise RuntimeError(
            "Collection is empty — run embed.py to build the index first."
        )

    query_embedding = _model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    for text, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "text": text,
            "source": meta["source"],
            "chunk_index": meta.get("chunk_index", -1),
            "distance": round(dist, 4),
        })

    return hits


# ---------------------------------------------------------------------------
# Main — build index and test with evaluation questions
# ---------------------------------------------------------------------------

EVAL_QUESTIONS = [
    "Which CS course do students consider the most time-consuming?",
    "Which course do students recommend for preparing for technical interviews?",
    "What topic do students report struggling with most in Algorithms?",
    "Which course places the greatest emphasis on teamwork and collaboration?",
    "Which course do students say is particularly useful for internships and practical industry skills?",
]

if __name__ == "__main__":
    build_index()

    print("\n--- Retrieval test: evaluation questions ---\n")
    for question in EVAL_QUESTIONS:
        print(f"Q: {question}")
        hits = retrieve(question)
        for i, r in enumerate(hits, 1):
            print(f"  [{i}] source={r['source']}  chunk={r['chunk_index']}  dist={r['distance']}")
            print(f"       {r['text'][:150]}...")
        print()
