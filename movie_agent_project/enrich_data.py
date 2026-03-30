import weaviate
from weaviate_agents.transformation import TransformationAgent
from weaviate_agents.transformation.classes.operation import Operations
import os
import time
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("Connecting to Weaviate Cloud...")
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=weaviate.auth.AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
        headers={
            "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
        }
    )

    try:
        print("Initializing Transformation Agent...")
        transformation_agent = TransformationAgent(
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

        print("Starting enrichment job for 'Movie' collection...")
        # The agent modifies data in-place. We instruct it to read 'overview' and populate 'marketing_pitch'.
        response = transformation_agent.update_all()
        workflow_id = response.workflow_id

        print(f"\n[+] Workflow started successfully! Workflow ID: {workflow_id}")
        
        # Demonstrating tracking the status through workflow ID
        print("\nWaiting for transformation to complete. Checking status...")
        while True:
            status = transformation_agent.get_status(workflow_id)
            print(f"Current Status: {status}")
            
            # The status usually returns strings like 'running', 'completed', 'failed' etc.
            status_str = str(status).lower()
            if any(s in status_str for s in ["completed", "failed", "done", "error"]):
                break
            
            time.sleep(3)

        print("\nEnrichment process finished!")
        print("You can verify the new 'marketing_pitch' properties by running a standard query or checking the UI.")

    except Exception as e:
        print(f"\n[!] An error occurred during the Transformation process: {e}")
        print("Ensure you are running against test data on Weaviate Cloud, and that you have valid API keys.")

    finally:
        client.close()

if __name__ == "__main__":
    main()
