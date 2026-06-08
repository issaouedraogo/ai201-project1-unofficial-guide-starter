"""
The Unofficial CS Guide — full RAG pipeline wired together.

Pipeline:
  documents/ (text files + scraped pages)
      ↓ ingest.py  →  documents/all_chunks.json
      ↓ embed.py   →  chroma_db/  (vector index)
      ↓ app.py     →  Streamlit chat interface

Run:
    streamlit run app.py
"""

import streamlit as st
from embed import build_index, retrieve, _get_collection
from generator import generate_response


# ---------------------------------------------------------------------------
# Ingestion — runs once on startup, cached so it doesn't re-run on every rerender
# ---------------------------------------------------------------------------

@st.cache_resource
def init_index() -> None:
    """
    Builds the ChromaDB index on first startup.
    Streamlit re-runs this file on every interaction, so @cache_resource
    ensures build_index() is only called once per server session.
    """
    collection = _get_collection()
    if collection.count() > 0:
        return
    build_index()


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="The Unofficial CS Guide",
    page_icon="📚",
    layout="centered",
)

st.title("📚 The Unofficial CS Guide")
st.caption("Ask about CS courses and professors — answers grounded in real student reviews.")

init_index()

# ---------------------------------------------------------------------------
# Sidebar — sources
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### Sources")
    st.markdown("""
- Reddit r/learnprogramming (×3)
- Reddit r/compsci
- COP 3502C reviews (UCF)
- COP 3503C reviews (UCF)
- CSC 241 reviews (DePaul)
- Prof. Kapp (NYU)
- Prof. Decker (Delaware)
- Prof. Mazidi (UT Dallas)
""")
    st.divider()
    st.caption("Answers are grounded in the loaded sources only. If the information isn't in the reviews, the guide will say so.")

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------

if prompt := st.chat_input("e.g. What do students say about COP 3502C workload?"):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Retrieve + generate
    with st.chat_message("assistant"):
        with st.spinner("Searching reviews..."):
            retrieved = retrieve(prompt)
            response = generate_response(prompt, retrieved)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
