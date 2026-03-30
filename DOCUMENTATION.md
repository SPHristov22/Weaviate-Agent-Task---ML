# Technical Documentation — Movie Explorer AI

**Project:** Movie Explorer AI
**Stack:** Python · Weaviate Cloud · Weaviate Agents SDK · OpenAI · Streamlit
**Date:** March 2026

---

## 1. Goal

The goal of this project is to demonstrate how to build an intelligent, natural-language search application using **Weaviate Cloud** and the **Weaviate Agents SDK**. The domain chosen is movies and reviews — a familiar, relatable dataset that makes it easy to evaluate the quality of the agent's responses.

Specifically, the project covers:

- Designing and populating two interconnected Weaviate collections.
- Using a **Query Agent** to handle natural-language queries over those collections, including semantic search, scalar filtering, multi-collection retrieval, and follow-up (context-aware) questions.
- Using a **Transformation Agent** to enrich existing data records in-place with AI-generated content.
- Wrapping everything in a simple **Streamlit** chat UI.

---

## 2. Architecture

```
┌──────────────────────────────────────────────┐
│                  User (Browser)              │
└────────────────────┬─────────────────────────┘
                     │  HTTP (localhost:8501)
┌────────────────────▼─────────────────────────┐
│              Streamlit App (app.py)           │
│  - Chat message history                       │
│  - Sidebar: connection button, demo queries   │
└────────────────────┬─────────────────────────┘
                     │  Python function call
┌────────────────────▼─────────────────────────┐
│           Agent Service (agent_service.py)    │
│  - Connects to Weaviate Cloud via REST/gRPC   │
│  - Instantiates QueryAgent with system prompt │
└─────────┬──────────────────────┬─────────────┘
          │                      │
┌─────────▼──────────┐  ┌────────▼──────────────┐
│   Weaviate Cloud   │  │   OpenAI API           │
│   (WCD)            │  │   - text-embedding-3   │
│   ┌────────────┐   │  │     (vectorization)    │
│   │   Movie    │   │  │   - GPT-4o             │
│   │ collection │   │  │     (agent reasoning,  │
│   └─────┬──────┘   │  │      generative search,│
│         │ ref      │  │      data enrichment)  │
│   ┌─────▼──────┐   │  └───────────────────────┘
│   │   Review   │   │
│   │ collection │   │
│   └────────────┘   │
└────────────────────┘
```

**Data flow for a user query:**

1. User types a question in the Streamlit chat.
2. `app.py` calls `query_agent.run(prompt)`.
3. The Query Agent sends the prompt to the OpenAI LLM, which decides what Weaviate query to issue (semantic, scalar filter, multi-collection, or hybrid).
4. Weaviate executes the query against the vector index and returns matching objects.
5. The LLM synthesizes a human-readable answer from the results.
6. The answer is displayed in the chat.

---

## 3. Data Collections

### 3.1 Movie

Created with `text2vec-openai` vectorizer and `gpt-4o` generative config.

| Property | Type | Notes |
|---|---|---|
| `title` | Text | Not vectorized by default |
| `director` | Text | Not vectorized by default |
| `overview` | Text | **Vectorized** — the main field for semantic search |
| `release_year` | Int | Used in scalar filters |
| `genre` | Text | Used in scalar filters |
| `rating` | Number | Used in scalar filters |
| `marketing_pitch` | Text | Populated by the Transformation Agent |

### 3.2 Review

| Property | Type | Notes |
|---|---|---|
| `review_text` | Text | **Vectorized** — used in semantic search across reviews |
| `sentiment` | Text | `"Positive"` or `"Negative"` |
| `hasMovie` | Cross-reference | Points to the related `Movie` object |

The cross-reference allows the Query Agent to perform **multi-collection queries** — e.g., "Find a sci-fi movie and show me its reviews" — in a single agent call.

### 3.3 Sample Data

The dataset is loaded by `data_loader.py` and contains:

- **20 movies** spanning genres: Sci-Fi, Action, Drama, Crime, Horror, Fantasy, Animation, Adventure, Historical, Comedy, Mystery, Thriller.
- **11 reviews**, each linked to one of the movies via `hasMovie`.

Selected movies include: *Inception*, *Interstellar*, *The Dark Knight*, *The Godfather*, *Parasite*, *The Matrix*, *Spirited Away*, *Mad Max: Fury Road*, *A Quiet Place*, and others.

---

## 4. Used Agents

### 4.1 Query Agent

**File:** `agent_service.py`
**Class:** `weaviate_agents.query.QueryAgent`

The Query Agent is the core of the application. It is initialized with:

- The Weaviate client (authenticated connection to WCD).
- The list of collections it is allowed to query: `["Movie", "Review"]`.
- A `system_prompt` that constrains its behavior:

> *"You are a helpful, expert movie assistant. Use exclusively the provided Weaviate collections (Movie, Review) to answer user questions. Provide clear, concise, and structured answers."*

At runtime, the agent:

1. Reads the schema of the specified collections.
2. Receives the user's natural-language prompt.
3. Uses the underlying LLM (GPT-4o) to decide which collection(s) to query and what kind of query to construct (vector search, scalar filter, hybrid, or multi-collection with cross-references).
4. Executes the query via the Weaviate v4 API.
5. Returns a `final_answer` string synthesized from the retrieved objects.

The agent also maintains **conversational context** within a session, enabling follow-up questions that reference previous results without the user needing to repeat details.

### 4.2 Transformation Agent

**File:** `enrich_data.py`
**Class:** `weaviate_agents.transformation.TransformationAgent`

The Transformation Agent enriches existing records in-place. It is configured with:

- The target collection: `"Movie"`.
- An operation that reads the `overview` property and writes a generated value to `marketing_pitch`:

```python
Operations.update_property(
    property_name="marketing_pitch",
    view_properties=["overview"],
    instruction="Write a short, engaging 1-sentence marketing pitch based on the movie overview."
)
```

The agent runs **asynchronously** via `update_all()`, which returns a `workflow_id`. The script polls the workflow status in a loop until it reaches a terminal state (`completed` / `failed`). This demonstrates the pattern of batch, background data enrichment — suitable for preparing production datasets.

---

## 5. Sample Inputs and Outputs

The Streamlit UI includes five pre-built demo queries that cover the main agent capabilities.

### Query 1 — Simple Semantic Search

**Input:** `"Find me a sci-fi movie about space anomalies."`

**What happens:** The agent vectorizes the query and finds the movie(s) whose `overview` embedding is closest in cosine similarity.

**Expected output:**
> *Interstellar (2014) — A team of explorers travel through a wormhole in space... Rating: 8.6*

---

### Query 2 — Multi-Collection Query

**Input:** `"Find me a sci-fi movie and also show me its reviews."`

**What happens:** The agent queries `Movie` for a semantic match, then follows the `hasMovie` cross-reference to retrieve linked `Review` objects.

**Expected output:**
> *Inception (2010) — [overview]*
>
> **Reviews:**
> - "Mind-bending and visually spectacular. Nolan at his finest." — Positive
> - "Too confusing for its own good. Left me with a headache." — Negative

---

### Query 3 — Follow-Up / Context-Aware Question

**Input:** `"What is the release year of the space movie you just mentioned?"`

**What happens:** The agent retains the context of the previous answer (e.g., *Interstellar*) and retrieves the `release_year` without requiring the user to repeat the title.

**Expected output:**
> *Interstellar was released in 2014.*

---

### Query 4 — Scalar Filtering and Aggregation

**Input:** `"Find action movies released before 2010 with a rating above 8.5."`

**What happens:** The LLM translates the intent into exact scalar filters: `genre = "Action"`, `release_year < 2010`, `rating > 8.5`.

**Expected output:**
> *The Dark Knight (2008) — Rating: 9.0*

---

### Query 5 — Free-Form / Abstract Formulation

**Input:** `"I'm in the mood for something nostalgic and slightly scary but no jump scares."`

**What happens:** There are no scalar fields for "nostalgic" or "no jump scares." The agent relies entirely on semantic (dense) retrieval against the `overview` embeddings.

**Expected output:**
> *A Quiet Place (2018) — Known for its tense, incredibly scary moments without jump scares.*

---

## 6. Data Processing Algorithms

### 6.1 Dense Vector Retrieval

Each time a text property marked for vectorization (`overview`, `review_text`) is inserted into Weaviate, the `text2vec-openai` module calls the OpenAI Embeddings API and stores the resulting vector alongside the object. At query time, the user's prompt is embedded with the same model and the database performs an **approximate nearest-neighbor (ANN)** search using cosine similarity (HNSW index). This enables semantic matching — finding conceptually related content even when exact keywords are absent.

### 6.2 LLM-Based Query Planning (Tool/Function Calling)

The Query Agent leverages the **function calling** capabilities of the underlying LLM. Weaviate exposes a set of "tools" (search, filter, fetch by reference, aggregate) to the LLM, which selects and parameterizes them based on the user's intent. This means the agent can:

- Combine vector search with scalar filters in a single query.
- Decide to query multiple collections and join results via cross-references.
- Produce aggregations (e.g., count, average rating) without explicit programming.

### 6.3 In-Place Data Transformation

The Transformation Agent iterates over all objects in the `Movie` collection and for each one calls the LLM with the specified `view_properties` as context. The generated value is written back to Weaviate in the `marketing_pitch` field. This is a **batch, asynchronous enrichment pipeline** with built-in workflow tracking.

---

## 7. Limitations and Future Development

### Current Limitations

| Area | Limitation |
|---|---|
| **Dataset size** | Only 20 movies. At scale, relevance tuning (Limit, Alpha for hybrid search) would be needed. |
| **Context window** | The Query Agent passes retrieved objects to the LLM; very large result sets may exceed token limits. |
| **Static data** | No mechanism to add new movies or reviews through the UI — only via scripts. |
| **No authentication** | The Streamlit app has no user login; API keys are loaded from a local `.env` file. |
| **Single-user session** | Chat history is stored in `st.session_state` and is not persisted between browser sessions. |
| **Sentiment is static** | Review sentiment is manually labelled in `data_loader.py`, not inferred automatically. |

### Ideas for Future Development

1. **Personalization Agent** — Track a user's query history and liked movies to re-rank results based on individual preferences (Weaviate Personalization Agent, Variant B of the task).
2. **Hybrid Search** — Combine dense vector search with BM25 keyword search (`alpha` parameter) to improve precision on title or director lookups.
3. **Dynamic data ingestion** — Add a UI form that lets users submit new movies or reviews, triggering both `data_loader` insertion and a Transformation Agent enrichment run.
4. **Automated sentiment analysis** — Replace the static `sentiment` labels with a Transformation Agent operation that infers sentiment from `review_text` automatically.
5. **Expanded dataset** — Integrate a public movie API (e.g., TMDB) to populate thousands of real movies and reviews, making the semantic search capabilities much more meaningful.
6. **Multi-user support** — Introduce session management and a backend store (Redis or a database) to persist chat history per user.
