import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import os
import time
import sys
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple

# Import our custom modules
import agent_utils
import logging_utils

# Configure enrichment pipeline logger
logger = logging_utils.get_pipeline_logger('enrichment')

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
    start_time = time.time()
    logger.info(f"Starting enrichment for domain: {domain}")
    
    # agent_utils.query_domain now handles exceptions internally and returns error info
    # So we don't need a try/except block here - the function will always return a result
    contact_info = agent_utils.query_domain(domain)
    
    # Log the outcome
    duration = time.time() - start_time
    if 'enrichment_error' in contact_info:
        logger.warning(f"Enrichment failed for {domain} after {duration:.2f}s: {contact_info['enrichment_error']}")
    else:
        logger.info(f"Successfully enriched {domain} in {duration:.2f}s")
        logger.info(f"Fields retrieved: {list(contact_info.keys())}")
    
    # Make sure domain is always included
    contact_info['company_domain'] = domain
    
    return contact_info

def already_processed_domains(output_csv_path: str) -> Set[str]:
    """
    Get a set of domains that have already been processed.
    
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
        domains = set(df['Company Domain (website url)'].astype(str))
        logger.info(f"Found {len(domains)} already processed domains in {output_csv_path}")
        return domains
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
        # Convert results to DataFrame
        results_df = pd.DataFrame(results)
        
        # Save final, complete results
        results_df.to_csv(output_csv, index=False)
        
        # Collect statistics for reporting
        all_columns = list(results_df.columns)
        enrichment_columns = [col for col in all_columns if col not in df.columns]
        
        # Report completion
        duration = (datetime.now() - start_time).total_seconds() / 60
        logger.info(f"=== Enrichment complete ===")
        logger.info(f"Duration: {duration:.2f} minutes")
        logger.info(f"Domains processed: {len(results)} of {total_unprocessed}")
        logger.info(f"Success: {succeeded}, Failed: {failed}")
        logger.info(f"Enrichment fields: {', '.join(enrichment_columns)}")
        
        print(f"\nEnrichment complete in {duration:.2f} minutes")
        print(f"Successfully enriched: {succeeded} domains")
        print(f"Failed: {failed} domains")
        print(f"Output written to: {output_csv}")
    else:
        logger.warning("No results were produced")
        print("No results were produced. Check logs for errors.")

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
