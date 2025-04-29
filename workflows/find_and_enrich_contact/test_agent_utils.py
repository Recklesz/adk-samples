#!/usr/bin/env python
"""
Test script for agent_utils module.

This script demonstrates how to use the agent_utils module
to query the FOMC research agent for contact information.
It's a simpler alternative to test_run_fomc_research.py.
"""

import os
import json
import logging
import argparse
import time
from dotenv import load_dotenv

# Import our agent utilities
import agent_utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_agent_utils')

def run_test(domain: str):
    """
    Run a test query against the FOMC research agent using agent_utils.
    
    Args:
        domain: The company domain to research
    """
    logger.info(f"Testing agent with domain: {domain}")
    
    # Record the start time
    start_time = time.time()
    
    try:
        # Call the agent through our utility module
        contact_info = agent_utils.query_domain(domain)
        
        # Calculate elapsed time
        elapsed = time.time() - start_time
        
        # Show the results
        logger.info(f"Query completed in {elapsed:.2f} seconds")
        logger.info(f"Contact info fields: {list(contact_info.keys())}")
        
        # Pretty print the contact info
        print("\n===== AGENT RESULTS =====")
        print(json.dumps(contact_info, indent=2))
        print("=========================\n")
        
        # Check if there's a contacts.csv file and show information about it
        contacts_path = agent_utils.get_contacts_csv_path()
        if os.path.exists(contacts_path):
            contacts = agent_utils.read_contacts_from_csv()
            logger.info(f"Total contacts in CSV: {len(contacts)}")
            
            # Show CSV headers
            if contacts:
                logger.info(f"CSV fields: {list(contacts[0].keys())}")
        
        return contact_info
        
    except Exception as e:
        logger.error(f"Error querying agent for {domain}: {e}")
        elapsed = time.time() - start_time
        logger.info(f"Failed after {elapsed:.2f} seconds")
        raise

def main():
    """Parse arguments and run the test"""
    parser = argparse.ArgumentParser(description="Test the agent_utils module with a domain")
    parser.add_argument('domain', type=str, help="Domain to query (e.g., elevenlabs.io)")
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Run the test
    run_test(args.domain)

if __name__ == "__main__":
    main()
