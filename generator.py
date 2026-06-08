"""
Milestone 5: Grounded response generation using Groq.

Accepts a user query and the retrieved chunks from embed.py,
builds a grounded prompt, and returns a response that cites
only the provided context — never outside knowledge.
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

_client = Groq(api_key=os.environ["GROQ_API_KEY"])

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a helpful assistant that answers questions about \
introductory computer science courses and professors using only the student \
reviews and forum discussions provided to you.

Rules you must follow:
- Answer using ONLY the information in the provided context passages.
- If the context does not contain enough information to answer the question, \
say so clearly — do not guess or use outside knowledge.
- After your answer, list the sources you drew from using the format: \
"Sources: <source_name>, <source_name>, ..."
- Keep your answer concise and focused on what students actually said."""


def generate_response(query: str, retrieved_chunks: list[dict]) -> str:
    """
    Builds a grounded prompt from the retrieved chunks and calls Groq.

    Each chunk is formatted as a numbered passage so the model can
    reference specific pieces of evidence rather than blending them.

    Args:
        query: the user's question
        retrieved_chunks: list of dicts with keys 'text', 'source', 'chunk_index'

    Returns:
        The model's grounded response as a string.
    """
    if not retrieved_chunks:
        return "I couldn't find any relevant information in the course and professor reviews to answer that question."

    # Format each chunk as a numbered passage with its source label
    context_blocks = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        source_label = chunk["source"].replace("_", " ")
        context_blocks.append(f"[{i}] ({source_label})\n{chunk['text']}")

    context = "\n\n".join(context_blocks)

    user_message = f"Context passages:\n\n{context}\n\nQuestion: {query}"

    response = _client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,  # low temperature for factual, grounded answers
        max_tokens=512,
    )

    return response.choices[0].message.content
