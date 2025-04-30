import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import os
import time
import sys
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple

# Import our custom modules
from runner import run_fomc_research
import logging_utils
import os

# Configure enrichment pipeline logger
logger = logging_utils.get_pipeline_logger('enrichment')

# Set up contact data directory (mimic agent_utils logic)
CONTACT_DATA_DIR = os.environ.get('CONTACT_DATA_PATH') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'contact_data'
)

def ensure_contact_data_dir_exists():
    os.makedirs(CONTACT_DATA_DIR, exist_ok=True)
    logger.info(f"Ensured contact data directory exists: {CONTACT_DATA_DIR}")
    return CONTACT_DATA_DIR

# Placeholder for your actual agent enrichment logic
# Replace this function with your real agent code
# It should return a dict with new fields to be added per row
def enrich_company(domain: str) -> Dict[str, Any]:
    """
    Enriches a company domain by finding contact information using the FOMC research agent.
    Args:
        domain: The company domain to enrich
    Returns:
        A dictionary with enriched fields from the agent (from the CSV)
    """
    import json
    start_time = time.time()
    logger.info(f"Starting enrichment for domain: {domain}")

    # Set up isolated run directory for this domain
    base_dir = ensure_contact_data_dir_exists()
    sanitized = domain.replace('.', '_').replace('/', '_')
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    run_dir = os.path.join(base_dir, f"{sanitized}_{ts}")
    os.makedirs(run_dir, exist_ok=True)
    logger.info(f"Run directory created for domain {domain}: {run_dir}")

    # Run the agent using the in-process runner
    try:
        new_contacts = run_fomc_research(domain, run_dir)
    except Exception as e:
        logger.error(f"Error running agent for {domain}: {e}", exc_info=True)
        return {
            'company_domain': domain,
            'enrichment_error': str(e),
            'enrichment_note': 'Agent processing failed, see logs for details'
        }

    logger.info(f"New contacts found: {len(new_contacts) if new_contacts else 0}")
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
    duration = time.time() - start_time
    logger.info(f"Completed enrichment for {domain} in {duration:.2f}s")
    return result


def already_processed_domains(output_csv_path: str) -> Set[str]:
    """
    Get a set of domains that have already been processed (i.e., have valid contact data).
    Domains with 'No contacts found by the agent' or blank contact fields will be retried.
    Args:
        output_csv_path: Path to the output CSV
    Returns:
        Set of domain strings that have already been processed
    """
    if not os.path.exists(output_csv_path):
        logger.info(f"No existing output CSV found at {output_csv_path}")
        return set()
    try:
        df = pd.read_csv(output_csv_path)
        processed = set()
        for _, row in df.iterrows():
            enrichment_note = str(row.get('enrichment_note', '')).strip()
            first = str(row.get('First Name', '')).strip()
            last = str(row.get('Last Name', '')).strip()
            email = str(row.get('Email', '')).strip()
            # Mark as processed if any contact field is present and not just a 'no contacts' note
            if (
                (first or last or email) and enrichment_note != 'No contacts found by the agent'
            ):
                processed.add(str(row['Company Domain (website url)']))
        logger.info(f"Found {len(processed)} successfully processed domains in {output_csv_path}")
        return processed
    except Exception as e:
        logger.warning(f"Error reading processed domains from {output_csv_path}: {e}", exc_info=True)
        return set()


def main(input_csv: str, output_csv: str, concurrency: int = 2) -> None:
    """
    Main enrichment pipeline function.
    
    Args:
        input_csv: Path to input CSV with company data
        output_csv: Path to output CSV where enriched data will be written
        concurrency: Number of parallel enrichment tasks
    """
    start_time = datetime.now()
    logger.info(f"=== Starting enrichment pipeline ===")
    logger.info(f"Input: {input_csv}")
    logger.info(f"Output: {output_csv}")
    logger.info(f"Concurrency: {concurrency} workers")
    
    # Read input data
    try:
        df = pd.read_csv(input_csv)
        logger.info(f"Read {len(df)} companies from {input_csv}")
    except Exception as e:
        logger.error(f"Failed to read input CSV {input_csv}: {e}", exc_info=True)
        print(f"Error: Could not read input CSV {input_csv}: {e}")
        return
    
    # Get already processed domains
    processed_domains = already_processed_domains(output_csv)
    
    # Prepare output DataFrame
    if os.path.exists(output_csv):
        try:
            enriched_df = pd.read_csv(output_csv)
            logger.info(f"Loaded existing output CSV with {len(enriched_df)} rows")
        except Exception as e:
            logger.warning(f"Error reading existing output CSV, creating new one: {e}", exc_info=True)
            enriched_df = pd.DataFrame(columns=df.columns)
    else:
        enriched_df = pd.DataFrame(columns=df.columns)
        logger.info("Created new output DataFrame")
    
    # Filter unprocessed rows
    unprocessed = df[~df['Company Domain (website url)'].astype(str).isin(processed_domains)]
    total_unprocessed = len(unprocessed)
    
    if total_unprocessed == 0:
        logger.info("No new companies to process")
        print("All companies have already been processed. Nothing to do.")
        return
    
    logger.info(f"Processing {total_unprocessed} new companies with {concurrency} workers")
    print(f"Processing {total_unprocessed} companies with {concurrency} concurrent workers...")
    rows = unprocessed.to_dict(orient='records')
    
    # Process each domain directly (one at a time in thread pool)
    # Our enrich_company function now handles errors internally
    def process_row(idx, row):
        domain = row['Company Domain (website url)']
        print(f"[{idx+1}/{total_unprocessed}] Processing: {domain}")
        
        enrichment = enrich_company(domain)
        row.update(enrichment)
        
        # Write checkpoint after each successful enrichment
        # This ensures we don't lose progress if something crashes
        if idx % 5 == 0 or idx == total_unprocessed - 1:
            # Add this completed row to a temporary results DataFrame
            temp_df = pd.DataFrame([row])
            # Append to the existing output file
            if os.path.exists(output_csv):
                temp_df.to_csv(output_csv, mode='a', header=False, index=False)
            else:
                temp_df.to_csv(output_csv, index=False)
            logger.info(f"Checkpointed progress after processing {idx+1} domains")
        
        return row
    
    # Process domains in parallel with progress tracking
    results = []
    succeeded = 0
    failed = 0
    
    # Use a shared lock for console output to avoid interleaving logs
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        # Submit all tasks and get futures
        future_to_idx = {}
        for i, row in enumerate(rows):
            # Small delay between submissions to avoid log collisions
            if i > 0:
                time.sleep(0.1)
            future = executor.submit(process_row, i, row)
            future_to_idx[future] = i
        
        # Process completed futures
        for future in concurrent.futures.as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                result = future.result()
                
                # Track success/failure
                if 'enrichment_error' in result:
                    failed += 1
                else:
                    succeeded += 1
                    
                results.append(result)
                
                # Calculate and display progress
                completed = succeeded + failed
                percent_done = (completed / total_unprocessed) * 100
                print(f"Progress: {completed}/{total_unprocessed} domains ({percent_done:.1f}%) - Success: {succeeded}, Failed: {failed}")
                
            except Exception as e:
                logger.error(f"Unhandled error processing domain at index {idx}: {e}", exc_info=True)
                failed += 1
    
    # Final processing - create a full output file
    if results:
        # Convert new results to DataFrame
        new_df = pd.DataFrame(results)
        # Merge with existing enriched_df to preserve previous rows
        merged_df = pd.concat([enriched_df, new_df], ignore_index=True)
        # Write merged DataFrame to CSV
        merged_df.to_csv(output_csv, index=False)
        
        # Report completion
        duration_min = (datetime.now() - start_time).total_seconds() / 60
        logger.info("=== Enrichment complete ===")
        logger.info(f"Duration: {duration_min:.2f} minutes")
        logger.info(f"Domains processed: {len(merged_df) - len(processed_domains)} of {total_unprocessed}")
        logger.info(f"Success: {succeeded}, Failed: {failed}")
        # Print summary to console
        print(f"\nEnrichment complete in {duration_min:.2f} minutes")
        print(f"Successfully enriched: {succeeded} domains")
        print(f"Failed: {failed} domains")
        print(f"Output written to: {output_csv}")
    else:
        logger.warning("No new results to merge. CSV remains unchanged.")
        print("No new domains were enriched. CSV was not modified.")

if __name__ == "__main__":
    import argparse
    
    # Create and configure arg parser
    parser = argparse.ArgumentParser(description="Enrich companies CSV with agent results.")
    parser.add_argument('--input_csv', type=str, default='companies_data_1.csv',
                      help="Path to input CSV with company data")
    parser.add_argument('--output_csv', type=str, default='companies_data_1_enriched.csv',
                      help="Path to output CSV where enriched data will be written")
    parser.add_argument('--concurrency', type=int, default=2,
                      help="Number of parallel enrichment tasks (agents to run at once)")
    
    # Parse arguments and run main function
    args = parser.parse_args()
    
    # Print header
    print("\n=== FOMC Research Enrichment Pipeline ===")
    print(f"Input: {args.input_csv}")
    print(f"Output: {args.output_csv}")
    print(f"Concurrency: {args.concurrency} workers\n")
    
    # Run the main pipeline
    try:
        main(args.input_csv, args.output_csv, args.concurrency)
    except KeyboardInterrupt:
        print("\nEnrichment process was interrupted by user.")
        logger.warning("Process interrupted by user")
    except Exception as e:
        print(f"\nError: Enrichment process failed: {e}")
        logger.error(f"Unhandled error in main process: {e}", exc_info=True)
