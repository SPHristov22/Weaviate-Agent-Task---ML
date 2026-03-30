import sys

# Allow running with `python app.py` — detects that Streamlit's runtime
# hasn't loaded yet and relaunches the script under `streamlit run`.
if __name__ == "__main__" and "streamlit.runtime.scriptrunner" not in sys.modules:
    import subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", __file__])
    sys.exit()

import streamlit as st
from agent_service import get_query_agent

# Initialize the Streamlit page
st.set_page_config(page_title="Movie Explorer AI", page_icon="🎬", layout="wide")

st.title("🎬 Movie Explorer AI")
st.markdown("Powered by **Weaviate Query Agent** & Weaviate Cloud (WCD)")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_connected" not in st.session_state:
    st.session_state.agent_connected = False
if "query_agent" not in st.session_state:
    st.session_state.query_agent = None

# --- Sidebar (Collection Info & Status) ---
with st.sidebar:
    st.header("⚙️ Agent Status")
    
    if st.button("🔌 Connect to Weaviate Cloud"):
        with st.spinner("Connecting to Weaviate..."):
            agent, client = get_query_agent()
            if agent:
                st.session_state.query_agent = agent
                st.session_state.agent_connected = True
                st.success("Connected successfully!")
            else:
                st.error("Failed to connect. Check `.env` API keys.")

    if st.session_state.agent_connected:
        st.info("✅ Query Agent is active and ready.")
        
        st.header("📂 Data Collections")
        st.markdown("""
        **1. Movie**
        - `title` (Text)
        - `director` (Text)
        - `overview` (Text / Vectorized)
        - `release_year` (Int)
        - `genre` (Text)
        - `rating` (Number)
        
        **2. Review**
        - `review_text` (Text / Vectorized)
        - `sentiment` (Text)
        - `hasMovie` (Cross-reference to Movie)
        """)
    else:
        st.warning("Please connect to Weaviate first.")

    st.header("📋 Required Queries Demo")
    st.markdown("Click below to auto-fill the chat input.")
    
    # The 5 specific required queries
    q1 = "Find me a sci-fi movie about space anomalies."
    q2 = "Find me a sci-fi movie and also show me its reviews."
    q3 = "What is the release year of the space movie you just mentioned?"
    q4 = "Find action movies released before 2010 with a rating above 8.5."
    q5 = "I'm in the mood for something nostalgic and slightly scary but no jump scares."
    
    if st.button("1. Simple Search"):
        st.session_state.demo_query = q1
    if st.button("2. Multi-collection Query"):
        st.session_state.demo_query = q2
    if st.button("3. Follow-up Question"):
        st.session_state.demo_query = q3
    if st.button("4. Filtering / Aggregating"):
        st.session_state.demo_query = q4
    if st.button("5. Free-form formulation"):
        st.session_state.demo_query = q5

# --- Main Chat Interface ---

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Manage pre-filled input from sidebar buttons
prompt = st.chat_input("Ask about movies or reviews...")
if "demo_query" in st.session_state:
    prompt = st.session_state.demo_query
    del st.session_state.demo_query

if prompt:
    if not st.session_state.agent_connected:
        st.error("Please connect to Weaviate in the sidebar first!")
    else:
        # 1. Show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Get Agent response
        with st.chat_message("assistant"):
            with st.spinner("Agent is thinking..."):
                try:
                    # Execute the Weaviate Query Agent
                    response = st.session_state.query_agent.run(prompt)
                    
                    # Extract the textual answer from the agent's response object
                    answer = response.final_answer if hasattr(response, 'final_answer') else str(response)
                    
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.error(f"Error querying the agent: {e}")
