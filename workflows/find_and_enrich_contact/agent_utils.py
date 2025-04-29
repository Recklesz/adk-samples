"""
Utilities for interacting with the FOMC research agent.
This module properly uses the Runner pattern as in test_run_fomc_research.py.
"""

import os
import uuid
import asyncio
import json
import csv
import glob
from pathlib import Path
import logging
from typing import Dict, Any, List, Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import FOMC research agent components
from fomc_research.agent import root_agent  # This is an async coroutine, not a class
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('agent_utils')

# Determine the contact data directory path
CONTACT_DATA_DIR = os.environ.get(
    'CONTACT_DATA_DIR', 
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'contact_data')
)

def ensure_contact_data_dir_exists():
    """Ensure the contact data directory exists"""
    if not os.path.exists(CONTACT_DATA_DIR):
        os.makedirs(CONTACT_DATA_DIR)
        logger.info(f"Created contact data directory: {CONTACT_DATA_DIR}")

def get_contacts_csv_path():
    """Get the path to the contacts CSV file"""
    return os.path.join(CONTACT_DATA_DIR, 'contacts.csv')

def read_contacts_from_csv() -> List[Dict[str, str]]:
    """
    Read contacts from the contacts CSV file.
    
    Returns:
        List of contact dictionaries
    """
    contacts_path = get_contacts_csv_path()
    if not os.path.exists(contacts_path):
        return []
    
    contacts = []
    with open(contacts_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            contacts.append(dict(row))
    
    return contacts

async def query_agent_for_domain(domain: str) -> Dict[str, Any]:
    """
    Query the FOMC research agent for contact information about a company domain.
    Uses the same pattern as in test_run_fomc_research.py.
    
    Args:
        domain: The company domain to research
        
    Returns:
        A dictionary with contact information extracted from the CSV
    """
    # Ensure contact data directory exists
    ensure_contact_data_dir_exists()
    
    # Get the path to contacts.csv (used by the agent's save_contact_to_csv tool)
    contact_data_path = get_contacts_csv_path()
    os.environ['CONTACT_DATA_DIR'] = os.path.dirname(contact_data_path)
    
    # Create the agent - root_agent is a coroutine that returns (agent, exit_stack)
    agent, exit_stack = await root_agent
    
    # Save the initial state of contacts.csv (if it exists)
    initial_contacts = read_contacts_from_csv()
    logger.info(f"Initial contacts count: {len(initial_contacts)}")
    
    # Set up the ADK Runner with services
    session_service = InMemorySessionService()
    artifact_service = InMemoryArtifactService()
    app_name = "fomc_research_runner"
    
    runner = Runner(
        agent=agent, 
        session_service=session_service, 
        artifact_service=artifact_service,
        app_name=app_name
    )
    
    # Generate IDs for this session
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    session_id = str(uuid.uuid4())
    
    # Create the session
    session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
    
    # Create the query content for the domain
    logger.info(f"Querying agent for domain: {domain}")
    user_content = types.Content(role='user', parts=[types.Part(text=domain)])
    
    # Run the agent and collect response
    response_text = ""
    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
            if hasattr(event, 'text') and event.text:
                response_text += event.text
            
        logger.info(f"Agent completed processing for domain: {domain}")
    except Exception as e:
        logger.error(f"Error running agent for {domain}: {e}")
        raise
    
    # Read the final state of contacts.csv to see what the agent added
    final_contacts = read_contacts_from_csv()
    
    # Find new contacts that weren't there before
    new_contacts = []
    for contact in final_contacts:
        if contact not in initial_contacts:
            new_contacts.append(contact)
    
    logger.info(f"New contacts found: {len(new_contacts)}")
    
    # If no new contacts were added to CSV but we got a response,
    # extract what we can from the text response
    if not new_contacts:
        logger.warning(f"No contacts added to CSV for {domain}, extracting from response text")
        # Extract basic info from domain
        result = {
            'company_domain': domain,
            'response_text': response_text,
            'enrichment_note': 'Extracted from agent response (no CSV entry)'
        }
        return result
    
    # Convert the first new contact to our return format
    # Add additional fields we need
    result = new_contacts[0]
    result['company_domain'] = domain
    
    # Add any additional contacts as a note
    if len(new_contacts) > 1:
        result['additional_contacts_count'] = len(new_contacts) - 1
        result['enrichment_note'] = f'Found {len(new_contacts)} contacts, returning the first one'
    
    return result

# Synchronous wrapper for the async function
def query_domain(domain: str) -> Dict[str, Any]:
    """
    Synchronous wrapper for query_agent_for_domain.
    
    Args:
        domain: The company domain to research
        
    Returns:
        A dictionary with contact information
    """
    return asyncio.run(query_agent_for_domain(domain))

if __name__ == "__main__":
    # Example usage
    domain = "elevenlabs.io"
    print(f"Testing agent with domain: {domain}")
    result = query_domain(domain)
    print(json.dumps(result, indent=2))
