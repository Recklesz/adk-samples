"""
Script to run the FOMC research agent with a specific company query.
"""

import os
import sys
import asyncio
import uuid
from pathlib import Path
from contextlib import AsyncExitStack
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types

# Add the parent directory of 'fomc_research' package to the Python path
# Assumes script is run from 'workflows/find_and_enrich_contact'
current_dir = Path(__file__).parent
agent_dir = current_dir.parent.parent / 'agents' / 'fomc-research'
sys.path.insert(0, str(agent_dir))

from fomc_research.agent import root_agent


async def main():
    """Run the FOMC research agent with a specific query."""
    print("Starting FOMC research agent with query: elevenlabs.io")
    
    # Get the agent and exit stack
    agent, exit_stack = await root_agent

    async with exit_stack: 
        try:
            # --- Set up Runner and Session --- 
            session_service = InMemorySessionService()
            artifact_service = InMemoryArtifactService()  # Initialize artifact service
            # Define IDs for the run (app_name needed for Runner)
            app_name = "fomc_research_runner"
            runner = Runner(
                agent=agent, 
                session_service=session_service, 
                artifact_service=artifact_service,  # Pass the artifact service
                app_name=app_name
            )
            
            # Define other IDs for the run
            user_id = "test_user_123"
            session_id = str(uuid.uuid4()) # Generate a unique session ID

            # ---> Create the session before using it <--- 
            session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)

            print("Sending company query...")
            response_text = ""
            # Set contact data path in the environment
            # This ensures the save_contact_to_csv tool saves to the correct location
            workflow_dir = Path(__file__).parent
            contact_data_path = workflow_dir / "contact_data"
            os.environ["CONTACT_DATA_PATH"] = str(contact_data_path)
            print(f"Setting contact data path to: {contact_data_path}")
            
            # Create input content object
            company_query = "elevenlabs.io"
            user_content = types.Content(role='user', parts=[types.Part(text=company_query)])

            # Call runner.run_async with IDs and content
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
                 # Accumulate text from events 
                 # Check for final response event specifically for cleaner output
                 if event.is_final_response() and event.content and event.content.parts:
                    response_text += event.content.parts[0].text
                 # Optional: handle other event types like tool calls/responses if needed
                 # elif event.type == ... :
                 #    print(f"Intermediate Event: {event}")
                     
            print(f"Agent Response: {response_text}")

        except Exception as e:
            print(f"An error occurred during agent interaction: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 