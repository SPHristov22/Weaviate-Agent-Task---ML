import weaviate
from weaviate_agents.query import QueryAgent
import os
from dotenv import load_dotenv

def get_query_agent():
    load_dotenv()

    try:
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=os.getenv("WEAVIATE_URL"),
            auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
            headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}
        )

        agent = QueryAgent(
            client=client,
            collections=["Movie", "Review"],
            system_prompt=(
                "You are a helpful, expert movie assistant. Use exclusively the provided "
                "Weaviate collections (Movie, Review) to answer user questions. "
                "Provide clear, concise, and structured answers."
            )
        )
        return agent, client
    except Exception as e:
        print(f"Error connecting to Weaviate: {e}")
        return None, None
