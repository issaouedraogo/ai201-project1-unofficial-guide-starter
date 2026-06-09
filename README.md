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

## Sample Chunks

The following 5 chunks are representative samples produced by `ingest.py` after cleaning and splitting the source documents.

**Chunk 1 — Source: `reddit_1_cs_courses_order`**
> CS50 in particular is the best of all the courses that I've done so far, including the in-person ones that I'm paying for.
> I agree. CS50 Is worth the time investment of all the online programming courses I've tried.

**Chunk 2 — Source: `reviews_cop3502c`**
> Be ready for it to kick you in the behind unless you're studying and working out your assignments almost daily. First big boy CS class at UCF

**Chunk 3 — Source: `reviews_cop3503c`**
> Don't fall behind, because you will not pass this class if you do. There is way too much course material for any sort of slacking. Stay around the curve and focus on the labs and easy assignments, these can set you up early to do well.

**Chunk 4 — Source: `reviews_prof_decker_delaware`**
> Decker is wonderful. He provides amazingly simple, brief, and clear notes. That and the lectures is all you need to pass the course. Covers good, complex examples in lecture that always mirror the homework.

**Chunk 5 — Source: `reviews_prof_mazidi_utdallas`**
> The lectures are organized and engaging. Assignments and tests are fair, with great resources like the professor's custom textbook and YouTube videos.

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via Sentence Transformers, running locally with no API key required.

**Production tradeoff reflection:** all-MiniLM-L6-v2 was chosen because it provides strong semantic search performance while being lightweight and fast enough to run on a laptop. For a production system serving real users at scale, I would consider models such as BAAI/bge-large-en or OpenAI's text-embedding-3-large. These models offer higher accuracy on nuanced text and longer context windows, which would help when student reviews span multiple sentences or contain indirect phrasing. The tradeoffs are higher computational cost, increased latency, and for API-hosted models, per-request pricing. Multilingual support would also become relevant if the system needed to serve students who post in languages other than English.

---

## Retrieval Test Results

For each query, the system embeds the question and returns the top-5 most similar chunks from ChromaDB using cosine similarity.

**Query 1: "What do students say about the difficulty of COP 3502C?"**

| Rank | Source | Chunk excerpt |
|---|---|---|
| 1 | `reviews_cop3502c` | Be ready for it to kick you in the behind unless you're studying and working out your assignments almost daily… |
| 2 | `reviews_cop3502c` | Szumlanski's class is very difficult, but very vital if you're looking to gain the knowledge you'd actually want for a job in the field… |
| 3 | `reviews_cop3502c` | Going into CS1 at the start of the semester, I knew this was going to be a challenging course… |
| 4 | `reviews_cop3502c` | This class is very difficult, but very vital if you're looking to gain the knowledge… |
| 5 | `reviews_cop3502c` | Lots of data structures and runtime analysis in this class… |

*Why these chunks are relevant:* All five chunks come directly from the COP 3502C review source. The source label prepended to each chunk during embedding ensured that the query matched these chunks over unrelated course reviews. The chunks consistently describe a steep difficulty curve requiring daily practice, which aligns with the expected answer.

**Query 2: "What is Professor Decker's teaching style like according to students?"**

| Rank | Source | Chunk excerpt |
|---|---|---|
| 1 | `reviews_prof_decker_delaware` | Decker is wonderful. He provides amazingly simple, brief, and clear notes. That and the lectures is all you need to pass the course… |
| 2 | `reviews_prof_decker_delaware` | I love professor Decker. As a comp sci major this class made me more excited for the rest of the program… |
| 3 | `reviews_prof_decker_delaware` | Had him for 304 and 481. I found both courses pretty difficult overall. For 304, I felt Prof. Decker did a good job giving us a lot of practice to help the concepts click… |
| 4 | `reviews_prof_decker_delaware` | He gives really hard homework, but his exams are actually fair. He always made sure to go over things more than once… |
| 5 | `reviews_prof_decker_delaware` | Homework usually takes me more than 8 hours on average to complete, and that's for every week… |

*Why these chunks are relevant:* The professor's name appears in the source label prepended to every chunk from that document, so semantic similarity to "Decker" and "teaching style" correctly surfaces all five results from his review page. The chunks describe his note quality, practice problems, homework difficulty, and exam fairness — directly matching what students observed.

**Query 3: "What do students recommend as the best first course in computer science?"**

| Rank | Source | Chunk excerpt |
|---|---|---|
| 1 | `reddit_1_cs_courses_order` | CS50 in particular is the best of all the courses that I've done so far, including the in-person ones that I'm paying for… |
| 2 | `reddit_2_cs_foundation` | I definitely recommend Harvard's CS50 since you can just do it for free online… |
| 3 | `reddit_4_intro_cs_design` | I did Harvard CS50 Intro to Comp Sci. We started off with C and clawed our way up… |
| 4 | `reddit_2_cs_foundation` | Take courses from big universities. CS61A and CS61B will give a really good foundation… |
| 5 | `reddit_1_cs_courses_order` | I recommend it because for my CS education, I'm doing a combination of the two approaches… |

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt instructs the model to answer using only the information in the provided context passages, and to explicitly say so if the context does not contain enough information to answer — rather than guessing or drawing on outside knowledge. The exact instruction is: _"Answer using ONLY the information in the provided context passages. If the context does not contain enough information to answer the question, say so clearly — do not guess or use outside knowledge."_

**How source attribution is surfaced in the response:** Each retrieved chunk is formatted as a numbered passage with its source label before being sent to the model, e.g. `[1] (COP 3502C CS I UCF) <chunk text>`. The system prompt then instructs the model to end every response with a "Sources:" line listing the source names it drew from. This forces the model to cite specific chunks rather than blending information anonymously.

---

## Query Interface

**Input field:** A single chat text input at the bottom of the page with placeholder text `e.g. What do students say about COP 3502C workload?`. The user types a natural language question and submits it by pressing Enter.

**Output field:** A Streamlit chat message rendered in the assistant bubble. The response is plain prose grounded in the retrieved chunks and ends with a `Sources:` line listing the source document names the model drew from.

**Sidebar:** Lists all 10 knowledge sources so users know the scope of the system before asking.

**Sample interaction transcript:**

> **User:** What do students say about the difficulty of COP 3502C?
>
> **Assistant:** According to student reviews, COP 3502C (Computer Science I at UCF) is considered a very challenging course. Students describe a steep learning curve with a fast pace, noting that you need to practice coding and work on assignments almost daily to keep up. The material is math and logic-heavy, covering data structures and runtime analysis using the C programming language. Despite the difficulty, students say the course is "very vital" for gaining real CS knowledge and that grading is fair if you put in consistent effort.
>
> Sources: reviews_cop3502c

---

## Example Responses

**Example 1 — In-scope query with source attribution:**

> **Query:** What is Professor Decker's teaching style like according to students?
>
> **Response:** Students describe Professor Decker as a joy to listen to who truly cares about his students. He provides simple, brief, and clear notes, and his lectures cover complex examples that mirror the homework. His exams are fair, though his homework is notably hard — one student reported spending more than 8 hours per week on assignments. He makes sure to repeat material if the class doesn't understand and tells students exactly what to expect on exams. Students strongly recommend attending every class, noting that skipping means not passing.
>
> Sources: reviews_prof_decker_delaware

**Example 2 — In-scope query with source attribution:**

> **Query:** What do students recommend as the best first course in computer science?
>
> **Response:** Harvard's CS50 is the most frequently recommended first course in computer science. Multiple students describe it as the best course they have taken, including better than in-person university courses. It is praised for its teaching style, David Malan's lectures, and its depth of coverage. It is available free online. Some students also mention UC Berkeley's CS61A and CS61B as strong foundation courses.
>
> Sources: reddit_1_cs_courses_order, reddit_2_cs_foundation, reddit_4_intro_cs_design

**Example 3 — Out-of-scope query (refusal response):**

> **Query:** What are the best restaurants near UCF campus?
>
> **Response:** The provided context passages do not contain any information about restaurants near UCF campus. I can only answer questions about introductory computer science courses and professors based on the student reviews and forum discussions in my knowledge base.
>
> Sources: (none)

---

## Evaluation Report

<!-- Run your 5 test questions through the app and fill in the actual system responses below. -->

| #   | Question                                                                 | Expected answer                                                                                                                     | System response (summarized)                                                                                                                  | Retrieval quality  | Response accuracy |
| --- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ----------------- |
| 1   | What do students say about the difficulty of COP 3502C?                  | Steep learning curve, fast pace requiring daily practice; "difficult but very vital"; fair grading with consistent effort required. | Relevant                                                                                                                                      | Accurate           |
| 2   | What advice do students give for preparing for a Data Structures course? | Practice coding daily, start projects early, review discrete math and basic algorithms.                                             | No specific advice found; retrieved chunks only contain the original question post, not the replies.                                          | Partially relevant | Inaccurate        |
| 3   | What is Professor Decker's teaching style like according to students?    | Gives many practice problems that help concepts click; courses are challenging overall.                                             | Delightful and engaging; clear brief notes, helpful lectures, hard homework but fair exams, willing to repeat material, cares about students. | Relevant           | Accurate          |
| 4   | What do students recommend as the best first course in computer science? | CS50 is most frequently recommended for its depth and teaching quality.                                                             | Harvard's CS50 is recommended for building a strong CS foundation; praised for its teaching style over other online courses.                  | Relevant           | Accurate          |
| 5   | How do students describe the workload in COP 3503C?                      | Manageable but assignment-heavy; programming assignments are challenging but doable.                                                | Students describe the workload in COP 3503C as having programming assignments that made the course not easy.                                  | Partially relevant | Partially accurate |

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
