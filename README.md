# Movie Explorer AI

A Streamlit chatbot that uses **Weaviate Query Agent** to answer natural-language questions about movies and reviews stored in Weaviate Cloud.

## What It Does

- **Chat interface** — ask questions like "Find me a sci-fi movie about space anomalies" or "Show me action movies rated above 8.5"
- **Query Agent** — automatically decides which Weaviate collections to search (Movie, Review, or both) and translates your question into the right query
- **Transformation Agent** — enriches movie data by generating a `marketing_pitch` for each movie using its overview (via `enrich_data.py`)
- **Cross-references** — reviews are linked to their movies, so multi-collection queries work out of the box

## Project Structure

```
movie_agent_project/
  app.py             # Streamlit chat UI
  agent_service.py   # Weaviate client + QueryAgent setup
  data_loader.py     # Creates collections & inserts sample data
  enrich_data.py     # TransformationAgent — adds marketing pitches
  requirements.txt
  .env.example
```

## Setup

1. **Clone the repo** and `cd` into `movie_agent_project/`.

2. **Create a virtual environment and install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure API keys** — copy `.env.example` to `.env` and fill in:
   ```
   WEAVIATE_URL=<your Weaviate Cloud cluster URL>
   WEAVIATE_API_KEY=<your Weaviate API key>
   OPENAI_API_KEY=<your OpenAI API key>
   ```

4. **Load sample data** (20 movies + 11 reviews):
   ```bash
   python data_loader.py
   ```

5. **(Optional) Enrich data** with AI-generated marketing pitches:
   ```bash
   python enrich_data.py
   ```

6. **Run the app:**
   ```bash
   python app.py
   ```
   This launches Streamlit at `http://localhost:8501`.

## Data Collections

### Movie
| Field | Type | Description |
|---|---|---|
| `title` | Text | Movie title |
| `director` | Text | Director name |
| `overview` | Text (vectorized) | Plot summary — used for semantic search |
| `release_year` | Int | Year of release |
| `genre` | Text | Genre (Sci-Fi, Action, Drama, etc.) |
| `rating` | Number | IMDb-style score (0–10) |
| `marketing_pitch` | Text | AI-generated pitch, populated by Transformation Agent |

### Review
| Field | Type | Description |
|---|---|---|
| `review_text` | Text (vectorized) | Full review text |
| `sentiment` | Text | Positive / Negative |
| `hasMovie` | Cross-reference | Link to the related `Movie` object |

The sample dataset includes **20 movies** and **11 reviews** across genres: Sci-Fi, Action, Drama, Crime, Horror, Fantasy, Animation, and more.

## Tech Stack

- **Weaviate Cloud** — vector database with `text2vec-openai` embeddings
- **weaviate-client[agents]** — Query Agent & Transformation Agent
- **Streamlit** — chat UI
- **OpenAI (GPT-4o)** — generative search & data enrichment

## Further Reading

See [DOCUMENTATION.md](DOCUMENTATION.md) for a full technical report covering architecture, agent design, sample query flows, and future development ideas.