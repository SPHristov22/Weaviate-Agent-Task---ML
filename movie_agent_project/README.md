# 🎬 Movie Explorer AI (Weaviate Agents Project)

This project demonstrates an intelligent application using **Weaviate Agents**. It operates on the "Movies/TV Series" domain and uses the Weaviate Python SDK v4 (`weaviate-client[agents]`).

## 📁 Repository Structure
- `data_loader.py`: Connects to Weaviate Cloud (WCD), creates `Movie` and `Review` collections, and populates them with sample data.
- `enrich_data.py`: Demonstrates the **Transformation Agent** (Variant A extension) by generating a `marketing_pitch` for each movie.
- `agent_service.py`: Initializes and returns the **Query Agent** with a pre-configured system prompt.
- `app.py`: A **Streamlit** Web UI providing a chat interface to interact with the Query Agent and pre-set buttons for the required 5 queries.

## ⚙️ Setup Instructions

### 1. Requirements
Ensure you have Python 3.9+ installed.
Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root directory (you can copy `.env.example`).
```env
WEAVIATE_URL="https://your-cluster.weaviate.network"
WEAVIATE_API_KEY="your-weaviate-api-key"
OPENAI_API_KEY="your-openai-api-key"
```

### 3. Execution Flow
Run the scripts in the following order:

**Step A: Initialize Data**
```bash
python data_loader.py
```
*Outputs:* Creates Collections and loads the sample data.

**Step B: Data Enrichment (Optional/Bonus)**
```bash
python enrich_data.py
```
*Outputs:* Uses the Transformation Agent to generate short pitches.

**Step C: Run the Application**
```bash
streamlit run app.py
```
*Outputs:* Opens the chat UI in your browser. Click "Connect to Weaviate Cloud" on the left panel, and then test the queries!

## 🎥 Video Demo Hints (For the grading 3-7 min video)
1. Show your `.env` file (make sure API keys are blurred/hidden or just show `.env.example`).
2. Run `data_loader.py` and show the terminal output so the grader sees the schemas are built.
3. Run `enrich_data.py` to highlight the **Transformation Agent Workflow ID** tracking.
4. Run `streamlit run app.py`, click Connect.
5. Click the 5 buttons in the sidebar one by one to demonstrate:
    - Simple Search
    - Multi-collection
    - Follow-up conversational memory
    - Filtering
    - Free-form intent
