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
from datetime import datetime
from typing import Dict, Any, List, Optional

# Import our custom logging utilities
import logging_utils

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import FOMC research agent components
import sys
import subprocess
from pathlib import Path

# Determine the contact data directory path
CONTACT_DATA_DIR = os.environ.get('CONTACT_DATA_PATH') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'contact_data'
)

def ensure_contact_data_dir_exists():
    """Ensure the contact data directory exists"""
    # Create the directory specified by CONTACT_DATA_PATH (if set) or default
    path = os.environ.get('CONTACT_DATA_PATH', CONTACT_DATA_DIR)
    os.makedirs(path, exist_ok=True)
    pipeline_logger = logging_utils.get_pipeline_logger("agent_utils")
    pipeline_logger.info(f"Ensured contact data directory exists: {path}")
    return path

def get_contacts_csv_path():
    """Get the path to the contacts CSV file"""
    base_path = os.environ.get('CONTACT_DATA_PATH', CONTACT_DATA_DIR)
    return os.path.join(base_path, 'contacts.csv')

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

def query_domain(domain: str) -> Dict[str, Any]:
    """
    Query the FOMC research agent for contact information about a domain.
    
    This function launches a separate Python process that runs test_run_fomc_research.py
    with the given domain. This avoids async issues by isolating each agent in its own process.
    
    Args:
        domain: The company domain to research
        
    Returns:
        A dictionary with contact information from the agent
    """
    # Get a domain-specific logger
    logger = logging_utils.get_agent_logger(domain)
    logger.info(f"==== Starting agent processing for domain: {domain} =====")
    
    # Set up isolated run directory for this domain
    base_dir = ensure_contact_data_dir_exists()
    sanitized = domain.replace('.', '_').replace('/', '_')
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    run_dir = os.path.join(base_dir, f"{sanitized}_{ts}")
    os.makedirs(run_dir, exist_ok=True)
    logger.info(f"Run directory created for domain {domain}: {run_dir}")
    # Prepare contacts file path and initial state (will be empty)
    contacts_file = os.path.join(run_dir, 'contacts.csv')
    initial_contacts = []
    
    # Determine the starting state of contacts.csv
    logger.info(f"Initial contacts in CSV: {len(initial_contacts)}")
    
    # Get the path to the test script
    script_dir = Path(__file__).parent
    test_script = script_dir / "test_run_fomc_research.py"
    
    # Set up the command to run the test script with the domain as an argument
    # We'll use a new process for each domain to avoid async issues
    cmd = [
        sys.executable,  # Current Python interpreter
        str(test_script),
        domain  # Pass domain as a command-line argument
    ]
    
    # Set up the environment variables
    env = os.environ.copy()
    env["CONTACT_DATA_PATH"] = run_dir
    
    # Run the command and capture output
    logger.info(f"Executing: {' '.join(cmd)}")
    start_time = datetime.now()
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        # Process the command output
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Command completed in {duration:.2f} seconds")
        logger.debug(f"Command stdout: {result.stdout[:500]}")
        
        if result.returncode != 0:
            logger.error(f"Command failed with code {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            return {
                'company_domain': domain,
                'enrichment_error': f"Agent process failed with code {result.returncode}",
                'enrichment_note': 'Agent processing failed, see logs for details'
            }
    
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after 120 seconds")
        return {
            'company_domain': domain,
            'enrichment_error': "Agent process timed out",
            'enrichment_note': 'Agent processing timed out after 120 seconds'
        }
        
    except Exception as e:
        logger.error(f"Error running agent for {domain}: {e}", exc_info=True)
        return {
            'company_domain': domain,
            'enrichment_error': str(e),
            'enrichment_note': 'Agent processing failed, see logs for details'
        }
    
    # Read final contacts from isolated CSV
    final_contacts = []
    if os.path.exists(contacts_file):
        with open(contacts_file, newline='') as csvf:
            reader = csv.DictReader(csvf)
            for row in reader:
                final_contacts.append(dict(row))
    new_contacts = final_contacts
     
    logger.info(f"New contacts found: {len(new_contacts)}")
    
    # Process and return the results
    if new_contacts:
        # Log the new contacts
        for i, contact in enumerate(new_contacts):
            logger.info(f"Contact {i+1}: {contact.get('First Name', '')} {contact.get('Last Name', '')} - {contact.get('Email', '')}")
        
        # Format the result (first contact)
        result = new_contacts[0].copy()
        result['company_domain'] = domain
        
        # Handle multiple contacts
        if len(new_contacts) > 1:
            result['additional_contacts_count'] = len(new_contacts) - 1
            result['enrichment_note'] = f'Found {len(new_contacts)} contacts, returning the first one'
    else:
        # No contacts found
        logger.warning(f"No contacts added to CSV for {domain}")
        result = {
            'company_domain': domain,
            'enrichment_note': 'No contacts found by the agent'
        }
    
    logger.info(f"==== Completed agent processing for domain: {domain} =====")
    return result

# Synchronous wrapper for the async function
# Define variables to be used in the main section
example_domain = "elevenlabs.io"

if __name__ == "__main__":
    # Example usage
    domain = "elevenlabs.io"
    print(f"Testing agent with domain: {domain}")
    result = query_domain(domain)
    print(json.dumps(result, indent=2))
