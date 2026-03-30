import weaviate
from weaviate_agents.transformation import TransformationAgent
from weaviate_agents.transformation.classes.operation import Operations
import os
import time
from dotenv import load_dotenv

TERMINAL_STATES = {"completed", "failed", "done", "error"}


def main():
    load_dotenv()

    print("Connecting to Weaviate Cloud...")
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
        headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}
    )

    try:
        agent = TransformationAgent(
            client=client,
            collection="Movie",
            operations=[
                Operations.update_property(
                    property_name="marketing_pitch",
                    view_properties=["overview"],
                    instruction="Write a short, engaging 1-sentence marketing pitch based on the movie overview."
                )
            ]
        )

        response = agent.update_all()
        workflow_id = response.workflow_id
        print(f"Workflow started. ID: {workflow_id}")

        while True:
            status = agent.get_status(workflow_id)
            print(f"Status: {status}")
            if any(s in str(status).lower() for s in TERMINAL_STATES):
                break
            time.sleep(3)

        print("Enrichment complete.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
