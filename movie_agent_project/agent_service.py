import weaviate
from weaviate_agents.query import QueryAgent
import os
from dotenv import load_dotenv

def get_query_agent():
    """
    Initializes and returns the Weaviate Query Agent along with the client.
    Be sure to close the client when done if used sequentially, but Streamlit
    might keep it open across sessions depending on configuration.
    """
    load_dotenv()
    
    try:
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv("WEAVIATE_URL"),
            auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
            headers={
                "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
            }
        )
        
        # Initialize Query Agent
        # The agent automatically discovers available collections and uses the LLM
        # to decide whether to query 'Movie' or 'Review' or both.
        agent = QueryAgent(
            client=client,
            collections=["Movie", "Review"],
            system_prompt="You are a helpful, expert movie assistant. Use exclusively the provided Weaviate collections (Movie, Review) to answer user questions. Provide clear, concise, and structured answers."
        )
        return agent, client
    except Exception as e:
        print(f"Error connecting to Weaviate: {e}")
        return None, None
