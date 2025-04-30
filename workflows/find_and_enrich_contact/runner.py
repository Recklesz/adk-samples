"""
Runner logic for FOMC research agent.
This module provides a reusable API for running the agent given a domain and contact data path.
"""

import os
import sys
import asyncio
import uuid
from pathlib import Path
from contextlib import AsyncExitStack
from datetime import datetime
from typing import List, Dict, Any
import logging
import csv

from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.genai import types

# Import the agent (assume fomc_research.agent.root_agent is importable)
current_dir = Path(__file__).parent
agent_dir = current_dir.parent.parent / 'agents' / 'fomc-research'
sys.path.insert(0, str(agent_dir))
from fomc_research.agent import create_agent


def _get_logger(contact_data_path: Path) -> logging.Logger:
    """Set up logging to file and console under the contact_data_path/logs directory."""
    log_dir = Path(contact_data_path) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / f"fomc_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logger = logging.getLogger(f"fomc_runner_{os.getpid()}")
    logger.setLevel(logging.DEBUG)
    # Avoid duplicate handlers
    if not logger.handlers:
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger

async def _run_fomc_research(domain: str, contact_data_path: Path) -> List[Dict[str, str]]:
    """
    Run the FOMC research agent for a given domain and contact data path.
    Returns a list of contact dicts (may be empty if none found).
    """
    logger = _get_logger(contact_data_path)
    logger.info(f"Starting FOMC research agent with query: {domain}")
    # Set environment for agent tools
    os.environ["CONTACT_DATA_PATH"] = str(contact_data_path)
    Path(contact_data_path).mkdir(parents=True, exist_ok=True)

    try:
        agent, exit_stack = await create_agent()
        async with exit_stack:
            session_service = InMemorySessionService()
            artifact_service = InMemoryArtifactService()
            app_name = "fomc_research_runner"
            runner = Runner(
                agent=agent,
                session_service=session_service,
                artifact_service=artifact_service,
                app_name=app_name
            )
            user_id = "fomc_runner_user"
            session_id = str(uuid.uuid4())
            session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id)
            user_content = types.Content(role='user', parts=[types.Part(text=domain)])
            response_text = ""
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=user_content):
                if event.is_final_response() and event.content and event.content.parts:
                    response_text += event.content.parts[0].text
                logger.debug(f"Event received: {event}")
            logger.info(f"Agent Response: {response_text}")
    except Exception as e:
        logger.exception("An error occurred during agent interaction")
        return []

    # After agent run, read contacts from CSV if available
    contacts_file = Path(contact_data_path) / 'contacts.csv'
    contacts = []
    if contacts_file.exists():
        with open(contacts_file, newline='') as csvf:
            reader = csv.DictReader(csvf)
            for row in reader:
                contacts.append(dict(row))
        logger.info(f"Found {len(contacts)} contacts in CSV")
    else:
        logger.warning(f"No contacts.csv file found at {contacts_file}")
    return contacts

def run_fomc_research(domain: str, contact_data_path: Path) -> List[Dict[str, str]]:
    """
    Synchronous wrapper for running the FOMC research agent.
    """
    return asyncio.run(_run_fomc_research(domain, contact_data_path))
