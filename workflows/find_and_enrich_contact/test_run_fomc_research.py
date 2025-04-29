"""
Test Script to run the FOMC research agent with a specific company query.
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
import logging
from datetime import datetime

# Add the parent directory of 'fomc_research' package to the Python path
# Assumes script is run from 'workflows/find_and_enrich_contact'
current_dir = Path(__file__).parent
agent_dir = current_dir.parent.parent / 'agents' / 'fomc-research'
sys.path.insert(0, str(agent_dir))

from fomc_research.agent import root_agent


async def main():
    """Run the FOMC research agent with a specific query."""
    
    # Get domain from command-line argument or use default
    domain = "elevenlabs.io"  # Default domain
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    
    # Ensure contact data directory exists and set environment variable early
    # First, check if CONTACT_DATA_PATH is already set (from parent process)
    contact_data_path = os.environ.get("CONTACT_DATA_PATH")
    if contact_data_path:
        contact_data_path = Path(contact_data_path)
    else:
        # Use default if not set by parent process
        workflow_dir = Path(__file__).parent
        contact_data_path = workflow_dir / "contact_data"
        os.environ["CONTACT_DATA_PATH"] = str(contact_data_path)
    
    # Ensure directory exists
    contact_data_path = Path(contact_data_path)
    contact_data_path.mkdir(parents=True, exist_ok=True)

    # Configure logging to file and console
    log_dir = contact_data_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / f"fomc_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_file_path),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    logger.info(f"Starting FOMC research agent with query: {domain}")
    
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

            logger.info("Sending company query...")
            response_text = ""
            # Set contact data path in the environment
            # This ensures the save_contact_to_csv tool saves to the correct location
            logger.info(f"Setting contact data path to: {contact_data_path}")
            
            # Create input content object using the domain argument
            company_query = domain
            user_content = types.Content(role='user', parts=[types.Part(text=company_query)])

            # Call runner.run_async with IDs and content
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
                 # Accumulate text from events 
                 # Check for final response event specifically for cleaner output
                 if event.is_final_response() and event.content and event.content.parts:
                    response_text += event.content.parts[0].text
                 # Log all events
                 logger.debug(f"Event received: {event}")
                 # Optional: handle and log other event types explicitly
                 # if not event.is_final_response():
                 #     logger.debug(f"Intermediate Event: {event}")
                     
            logger.info(f"Agent Response: {response_text}")

        except Exception as e:
            logger.exception("An error occurred during agent interaction")


if __name__ == "__main__":
    # Print a startup message
    print(f"Running FOMC research agent with query: {sys.argv[1] if len(sys.argv) > 1 else 'elevenlabs.io'}")
    # Run the main function
    asyncio.run(main())