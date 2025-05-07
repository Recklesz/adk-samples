"""Simple enricher agent implementation."""

import csv
import logging
from pathlib import Path
from typing import AsyncIterable

from google.adk.agents import BaseAgent
from google.adk.events import Event, EventActions
from google.genai import types

# Configure logging
logger = logging.getLogger(__name__)

# Constants
INPUT_CSV = Path(__file__).parent.parent.parent.parent / "companies_data_1.csv"
DOMAIN_COLUMN_HEADER = "website_domain"

class SimpleEnricherAgent(BaseAgent):
    """Reads the first domain from the CSV, simulates enrichment, and yields/logs the result."""

    async def _run_async_impl(self, ctx) -> AsyncIterable[Event]:
        logger.info(f"Reading first data row from: {INPUT_CSV}")
        try:
            with open(INPUT_CSV, mode='r', newline='', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                if DOMAIN_COLUMN_HEADER not in reader.fieldnames:
                    error_msg = f"Column '{DOMAIN_COLUMN_HEADER}' not found in {INPUT_CSV}"
                    logger.error(error_msg)
                    yield Event(
                        author=self.name,
                        content=types.Content(role=self.name, parts=[types.Part(text=f"Error: {error_msg}")]),
                        actions=EventActions()
                    )
                    return
                first_data_row = next(reader, None)
                if first_data_row:
                    domain = first_data_row.get(DOMAIN_COLUMN_HEADER)
                    if domain:
                        logger.info(f"Simulating enrichment for domain: {domain}")
                        dummy_result = f"Successfully enriched data for {domain} (MVP simulation)"
                        yield Event(
                            author=self.name,
                            content=types.Content(role=self.name, parts=[types.Part(text=f"Enrichment simulation complete for {domain}. Result: {dummy_result}")]),
                            actions=EventActions(state_delta={"enrichment_result": dummy_result})
                        )
                    else:
                        logger.warning(f"Domain column '{DOMAIN_COLUMN_HEADER}' is empty in the first data row.")
                        yield Event(
                            author=self.name,
                            content=types.Content(role=self.name, parts=[types.Part(text="Warning: Domain empty in first row.")]),
                            actions=EventActions()
                        )
                else:
                    logger.warning(f"CSV file '{INPUT_CSV}' is empty or contains only a header.")
                    yield Event(
                        author=self.name,
                        content=types.Content(role=self.name, parts=[types.Part(text="Warning: Input CSV empty or header-only.")]),
                        actions=EventActions()
                    )
        except FileNotFoundError:
            logger.error(f"Input CSV file not found: {INPUT_CSV}")
            yield Event(
                author=self.name,
                content=types.Content(role=self.name, parts=[types.Part(text=f"Error: Input file not found at {INPUT_CSV}")]),
                actions=EventActions()
            )
        except Exception as e:
            logger.exception(f"Error reading CSV: {e}")
            yield Event(
                author=self.name,
                content=types.Content(role=self.name, parts=[types.Part(text=f"Error reading CSV: {e}")]),
                actions=EventActions()
            )


# Create an instance of the agent
simple_enricher_agent = SimpleEnricherAgent(name="simple_enricher")
