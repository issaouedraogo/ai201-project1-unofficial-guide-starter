# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section _after_ you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

This system covers computer science course and professor advice — student reviews, Reddit discussions, and professor ratings for introductory CS courses. The knowledge is valuable because official course descriptions and syllabi do not reflect teaching style, exam difficulty, workload, or what students actually struggle with. Students rely on informal peer advice to make course decisions, but that advice is scattered across forums and review sites with no single place to ask questions and get grounded answers.

---

## Document Sources

| #   | Source                                             | Type           | URL or file path                                           |
| --- | -------------------------------------------------- | -------------- | ---------------------------------------------------------- |
| 1   | Reddit r/learnprogramming                          | Forum thread   | https://www.reddit.com/r/learnprogramming/comments/fls11e  |
| 2   | Reddit r/learnprogramming                          | Forum thread   | https://www.reddit.com/r/learnprogramming/comments/1n23o6a |
| 3   | Reddit r/learnprogramming                          | Forum thread   | https://www.reddit.com/r/learnprogramming/comments/dx206v  |
| 4   | Reddit r/compsci                                   | Forum thread   | https://www.reddit.com/r/compsci/comments/hh8ijq           |
| 5   | COP 3502C (Computer Science I) reviews             | Course reviews | https://www.ratemycourses.io/ucf/course/cop3502c           |
| 6   | COP 3503C (Computer Science II) reviews            | Course reviews | https://www.ratemycourses.io/ucf/course/cop3503c           |
| 7   | CSC 241 Introduction to Computer Science I reviews | Course reviews | https://www.ratemycourses.io/depaul/course/csc241          |
| 8   | Professor reviews (Craig Kapp, NYU)                | Prof reviews   | https://www.ratemyprofessors.com/professor/1579749         |
| 9   | Professor reviews (Keith Decker, Delaware)         | Prof reviews   | https://www.ratemyprofessors.com/professor/540363          |
| 10  | Professor reviews (Karen Mazidi, UT Dallas)        | Prof reviews   | https://www.ratemyprofessors.com/professor/2190788         |

---

## Chunking Strategy

**Chunk size:** 300 characters

**Overlap:** 50 characters

**Why these choices fit your documents:** The corpus consists primarily of short student reviews, Reddit comments, and forum replies — each typically expressing one opinion or piece of advice in a few sentences. A 300-character chunk is large enough to preserve a complete thought while remaining small enough for precise retrieval. A 50-character overlap prevents key information from being lost when a sentence falls near a chunk boundary. Before chunking, documents were cleaned to remove HTML tags, navigation elements, ad text, cookie banners, and boilerplate phrases (e.g. "Rate My Courses", "Read more", "Comments on the course") that appear on every page but carry no review content.

**Final chunk count:** 136 chunks across all 10 sources

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via Sentence Transformers, running locally with no API key required.

**Production tradeoff reflection:** all-MiniLM-L6-v2 was chosen because it provides strong semantic search performance while being lightweight and fast enough to run on a laptop. For a production system serving real users at scale, I would consider models such as BAAI/bge-large-en or OpenAI's text-embedding-3-large. These models offer higher accuracy on nuanced text and longer context windows, which would help when student reviews span multiple sentences or contain indirect phrasing. The tradeoffs are higher computational cost, increased latency, and for API-hosted models, per-request pricing. Multilingual support would also become relevant if the system needed to serve students who post in languages other than English.

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt instructs the model to answer using only the information in the provided context passages, and to explicitly say so if the context does not contain enough information to answer — rather than guessing or drawing on outside knowledge. The exact instruction is: _"Answer using ONLY the information in the provided context passages. If the context does not contain enough information to answer the question, say so clearly — do not guess or use outside knowledge."_

**How source attribution is surfaced in the response:** Each retrieved chunk is formatted as a numbered passage with its source label before being sent to the model, e.g. `[1] (COP 3502C CS I UCF) <chunk text>`. The system prompt then instructs the model to end every response with a "Sources:" line listing the source names it drew from. This forces the model to cite specific chunks rather than blending information anonymously.

---

## Evaluation Report

<!-- Run your 5 test questions through the app and fill in the actual system responses below. -->

| #   | Question                                                                 | Expected answer                                                                                                                     | System response (summarized)                                                                                                                  | Retrieval quality  | Response accuracy |
| --- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ----------------- |
| 1   | What do students say about the difficulty of COP 3502C?                  | Steep learning curve, fast pace requiring daily practice; "difficult but very vital"; fair grading with consistent effort required. | Relevant                                                                                                                                      | Accurate           |
| 2   | What advice do students give for preparing for a Data Structures course? | Practice coding daily, start projects early, review discrete math and basic algorithms.                                             | No specific advice found; retrieved chunks only contain the original question post, not the replies.                                          | Partially relevant | Inaccurate        |
| 3   | What is Professor Decker's teaching style like according to students?    | Gives many practice problems that help concepts click; courses are challenging overall.                                             | Delightful and engaging; clear brief notes, helpful lectures, hard homework but fair exams, willing to repeat material, cares about students. | Relevant           | Accurate          |
| 4   | What do students recommend as the best first course in computer science? | CS50 is most frequently recommended for its depth and teaching quality.                                                             | Harvard's CS50 is recommended for building a strong CS foundation; praised for its teaching style over other online courses.                  | Relevant           | Accurate          |
| 5   | How do students describe the workload in COP 3503C?                      | Manageable but assignment-heavy; programming assignments are challenging but doable.                                                | No information found; only a Reddit source was returned with general tips like attending office hours.                                        | Off-target         | Inaccurate        |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** How do students describe the workload in COP 3503C?

**What the system returned:** The system said there was no information about COP 3503C workload and returned only a Reddit source with general tips (attending office hours, researching topics independently).

**Root cause (tied to a specific pipeline stage):** The failure occurred at the retrieval stage. The COP 3503C chunks exist in the vector index, but the query term "workload" does not appear in those reviews — students used words like "assignments", "difficulty", and "challenging" instead. Because all-MiniLM-L6-v2 embeds the query and chunks independently, this vocabulary gap reduced the cosine similarity between the query and the relevant chunks below the similarity of unrelated Reddit chunks that happened to mention effort and study habits. The model correctly refused to fabricate an answer, but retrieval never surfaced the right material.

**What you would change to fix it:** A query expansion step before retrieval — replacing or augmenting "workload" with synonyms like "assignments", "difficulty", and "how much work" — would increase the chance of matching the actual vocabulary in the reviews. Alternatively, using a larger embedding model with stronger semantic generalization (such as BAAI/bge-large-en) might bridge the vocabulary gap without explicit expansion.

---

## Spec Reflection

**One way the spec helped you during implementation:** The Chunking Strategy section of planning.md gave a concrete target — 300-character chunks with 50-character overlap — that I could hand directly to an AI tool to generate the `chunk_text()` function. Having the numbers decided in advance meant I could verify the output immediately by printing sample chunks and measuring their lengths, rather than tuning parameters during implementation.

**One way your implementation diverged from the spec, and why:** The spec described using FAISS or Chroma for the vector store, but the implementation settled on ChromaDB with a persistent client. More significantly, the spec did not anticipate that the embedding model would fail to distinguish between COP 3502C and COP 3503C chunks because the boilerplate filter stripped the page title — the only line containing the course number. To fix this, a source label was prepended to every chunk before embedding, which was not part of the original chunking or embedding plan.

---

## AI Usage

**Instance 1**

- _What I gave the AI:_ The Documents section of planning.md (10 sources including Reddit threads and review pages), the Chunking Strategy section (300-character chunks, 50-character overlap), and the pipeline diagram showing the five stages.
- _What it produced:_ A complete `ingest.py` script with `fetch_reddit_thread()`, `fetch_review_page()`, `clean_text()`, and `chunk_text()` functions, plus a `main()` that saves raw and chunked output per source.
- _What I changed or overrode:_ The Reddit fetcher initially used the public `.json` API, which returned 403 errors because Reddit blocked unauthenticated access. The Reddit sources were replaced with manually saved `.txt` files. The `clean_text()` function was also extended with an explicit blocklist of boilerplate phrases after ad text ("EssayPal.ai") leaked into the first chunk of the COP 3502C output.

**Instance 2**

- _What I gave the AI:_ The Retrieval Approach section of planning.md (all-MiniLM-L6-v2, top-k=5) and the architecture diagram showing the embedding and retrieval stage.
- _What it produced:_ An `embed.py` script with `build_index()` and `retrieve()` functions using SentenceTransformers and a persistent ChromaDB collection with cosine similarity.
- _What I changed or overrode:_ After testing with the evaluation questions, retrieval failed to distinguish COP 3502C from COP 3503C chunks because the course name was stripped during cleaning. A source label dictionary was added to prepend a human-readable course or source name to every chunk before embedding, which was not in the original spec.
