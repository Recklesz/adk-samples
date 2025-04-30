"""
Test Script to run the FOMC research agent with a specific company query using the shared runner API.
"""

import sys
import os
from pathlib import Path
import argparse
import json
from runner import run_fomc_research

def main():
    parser = argparse.ArgumentParser(description="Run the FOMC research agent for a company domain.")
    parser.add_argument('domain', type=str, nargs='?', default="elevenlabs.io", 
                        help="Domain to query (default: elevenlabs.io)")
    parser.add_argument('--contact-data-path', type=str, default=None, 
                        help="Optional path for contact data output (default: ./contact_data)")
    args = parser.parse_args()

    domain = args.domain
    contact_data_path = args.contact_data_path or (Path(__file__).parent / "contact_data")
    contact_data_path = Path(contact_data_path)
    contact_data_path.mkdir(parents=True, exist_ok=True)

    print(f"Running FOMC research agent with query: {domain}")
    try:
        contacts = run_fomc_research(domain, contact_data_path)
        if contacts:
            print("\n===== AGENT RESULTS =====")
            print(json.dumps(contacts, indent=2))
            print("=========================\n")
        else:
            print("No contacts found.")
    except Exception as e:
        print(f"Error running agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()