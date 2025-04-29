import pandas as pd
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import logging
import time
from typing import Dict, Any, List, Set

# Import our agent utilities
import agent_utils

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('enrichment')

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
    logger.info(f"Querying FOMC research agent for domain: {domain}")
    
    try:
        # Call the real agent through our utility module's synchronous wrapper
        # This function properly uses the Runner pattern from test_run_fomc_research.py
        contact_info = agent_utils.query_domain(domain)
        
        logger.info(f"Agent returned contact info for {domain}: {list(contact_info.keys())}")
        
        # Make sure the domain is included (though agent_utils should already do this)
        contact_info['company_domain'] = domain
        
        # The contact info should come from the CSV that the agent writes to
        # and will have fields like First Name, Last Name, Email, LinkedIn URL, etc.
        return contact_info
        
    except Exception as e:
        logger.error(f"Error querying agent for {domain}: {e}")
        # Retry logic in main() will handle this
        raise e

def already_processed_domains(output_csv_path: str) -> Set[str]:
    """
    Get a set of domains that have already been processed.
    
    Args:
        output_csv_path: Path to the output CSV
        
    Returns:
        Set of domain strings that have already been processed
    """
    if not os.path.exists(output_csv_path):
        return set()
    try:
        df = pd.read_csv(output_csv_path)
        return set(df['Company Domain (website url)'].astype(str))
    except Exception as e:
        logger.warning(f"Error reading processed domains from {output_csv_path}: {e}")
        return set()

def main(input_csv: str, output_csv: str, concurrency: int = 2, max_retries: int = 3) -> None:
    """
    Main enrichment pipeline function.
    
    Args:
        input_csv: Path to input CSV with company data
        output_csv: Path to output CSV where enriched data will be written
        concurrency: Number of parallel enrichment tasks
        max_retries: Maximum number of retries for failed enrichments
    """
    logger.info(f"Starting enrichment pipeline: {input_csv} → {output_csv} (concurrency={concurrency})")
    
    # Read input data
    try:
        df = pd.read_csv(input_csv)
        logger.info(f"Read {len(df)} companies from {input_csv}")
    except Exception as e:
        logger.error(f"Failed to read input CSV {input_csv}: {e}")
        return
    
    # Get already processed domains
    processed_domains = already_processed_domains(output_csv)
    logger.info(f"Found {len(processed_domains)} already processed domains")
    
    # Prepare output DataFrame
    if os.path.exists(output_csv):
        try:
            enriched_df = pd.read_csv(output_csv)
            logger.info(f"Loaded existing output CSV with {len(enriched_df)} rows")
        except Exception as e:
            logger.warning(f"Error reading existing output CSV, creating new one: {e}")
            enriched_df = pd.DataFrame(columns=df.columns)
    else:
        enriched_df = pd.DataFrame(columns=df.columns)
        logger.info("Created new output DataFrame")
    
    # Filter unprocessed rows
    unprocessed = df[~df['Company Domain (website url)'].astype(str).isin(processed_domains)]
    if len(unprocessed) == 0:
        logger.info("No new companies to process")
        return
    
    logger.info(f"Processing {len(unprocessed)} new companies with {concurrency} workers")
    rows = unprocessed.to_dict(orient='records')
    
    # Track all enrichment fields we encounter
    all_enrichment_fields = set()
    
    def enrich_and_merge(row):
        domain = row['Company Domain (website url)']
        logger.info(f"Processing domain: {domain}")
        
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                enrichment = enrich_company(domain)
                duration = time.time() - start_time
                
                # Update all_enrichment_fields with keys from this enrichment
                nonlocal all_enrichment_fields
                all_enrichment_fields.update(enrichment.keys())
                
                # Update row with enrichment data
                row.update(enrichment)
                logger.info(f"Successfully enriched {domain} in {duration:.2f}s")
                return row
            except Exception as e:
                logger.warning(f"Attempt {attempt+1}/{max_retries} failed for {domain}: {e}")
                if attempt == max_retries - 1:
                    # Last attempt failed, mark as error
                    row['enrichment_error'] = str(e)
                    logger.error(f"All attempts failed for {domain}: {e}")
                else:
                    # Wait before retrying (exponential backoff)
                    time.sleep(2 ** attempt)
        return row
    
    # Process in parallel
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        results = list(executor.map(enrich_and_merge, rows))
    
    if results:
        # Ensure all enrichment fields exist in the DataFrame
        results_df = pd.DataFrame(results)
        
        # Make sure all columns from both DataFrames are preserved
        all_columns = set(enriched_df.columns).union(results_df.columns)
        for col in all_columns:
            if col not in enriched_df.columns:
                enriched_df[col] = None
            if col not in results_df.columns:
                results_df[col] = None
        
        # Concatenate and save
        enriched_df = pd.concat([enriched_df, results_df], ignore_index=True)
        enriched_df.to_csv(output_csv, index=False)
        logger.info(f"Enrichment complete. Added {len(results)} rows to {output_csv}")
        logger.info(f"Enrichment fields found: {', '.join(sorted(all_enrichment_fields))}")
    else:
        logger.info("No results to write")
    
    print(f"Enrichment complete. Output written to {output_csv}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Enrich companies CSV with agent results.")
    parser.add_argument('--input_csv', type=str, default='companies_data_1.csv',
                      help="Path to input CSV with company data")
    parser.add_argument('--output_csv', type=str, default='companies_data_1_enriched.csv',
                      help="Path to output CSV where enriched data will be written")
    parser.add_argument('--concurrency', type=int, default=2,
                      help="Number of parallel enrichment tasks")
    parser.add_argument('--max_retries', type=int, default=3,
                      help="Maximum number of retries for failed enrichments")
    args = parser.parse_args()
    main(args.input_csv, args.output_csv, args.concurrency, args.max_retries)
