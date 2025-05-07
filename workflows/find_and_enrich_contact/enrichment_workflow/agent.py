import csv
import logging
import secrets
from pathlib import Path
from typing import AsyncIterable

from google.adk.agents import BaseAgent, SequentialAgent
from google.adk.events import Event, EventActions
from google.genai import types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
INPUT_CSV = Path(__file__).parent / "companies_data_1.csv"
OUTPUT_CSV = Path(__file__).parent / "output_mvp.csv"
DOMAIN_COLUMN_HEADER = "website_domain"

class CsvReaderAgent(BaseAgent):
    """Reads the first data row from the input CSV and extracts the domain."""

    async def _run_async_impl(self, ctx: AgentContext) -> AsyncIterable[Event]:
        logger.info(f"Reading first data row from: {INPUT_CSV}")
        try:
            with open(INPUT_CSV, mode='r', newline='', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                # Ensure the domain column exists
                if DOMAIN_COLUMN_HEADER not in reader.fieldnames:
                    error_msg = f"Column '{DOMAIN_COLUMN_HEADER}' not found in {INPUT_CSV}"
                    logger.error(error_msg)
                    yield Event(
                        author=self.name,
                        content=types.Content(role=self.name, parts=[types.Part(text=f"Error: {error_msg}")]),
                        actions=EventActions(error=True, escalate=True) # Escalate to stop workflow
                    )
                    return # Stop processing

                # Read the first data row (skip header)
                first_data_row = next(reader, None)

                if first_data_row:
                    domain = first_data_row.get(DOMAIN_COLUMN_HEADER)
                    if domain:
                        run_id = secrets.token_hex(4)
                        task_key = f"task:{run_id}:0" # Index 0 for the first row
                        state_delta = {
                            "run_id": run_id,
                            task_key: domain
                        }
                        logger.info(f"Extracted domain '{domain}' for run_id '{run_id}'")
                        yield Event(
                            author=self.name,
                            content=types.Content(role=self.name, parts=[types.Part(text=f"Processing domain: {domain}")]),
                            actions=EventActions(state_delta=state_delta)
                        )
                    else:
                        logger.warning(f"Domain column '{DOMAIN_COLUMN_HEADER}' is empty in the first data row.")
                        yield Event(
                            author=self.name,
                            content=types.Content(role=self.name, parts=[types.Part(text="Warning: Domain empty in first row.")]),
                            actions=EventActions(escalate=True) # Stop if no domain
                         )
                else:
                    logger.warning(f"CSV file '{INPUT_CSV}' is empty or contains only a header.")
                    yield Event(
                        author=self.name,
                        content=types.Content(role=self.name, parts=[types.Part(text="Warning: Input CSV empty or header-only.")]),
                        actions=EventActions(escalate=True) # Stop if no data
                    )

        except FileNotFoundError:
            logger.error(f"Input CSV file not found: {INPUT_CSV}")
            yield Event(
                author=self.name,
                content=types.Content(role=self.name, parts=[types.Part(text=f"Error: Input file not found at {INPUT_CSV}")]),
                actions=EventActions(error=True, escalate=True)
            )
        except Exception as e:
            logger.exception(f"Error reading CSV: {e}")
            yield Event(
                author=self.name,
                content=types.Content(role=self.name, parts=[types.Part(text=f"Error reading CSV: {e}")]),
                actions=EventActions(error=True, escalate=True)
            )


class SimpleEnricherAgent(BaseAgent):
    """Placeholder agent that simulates enrichment for the domain."""

    async def _run_async_impl(self, ctx: AgentContext) -> AsyncIterable[Event]:
        run_id = ctx.session.state.get("run_id")
        if not run_id:
            logger.error("run_id not found in session state.")
            yield Event(author=self.name, content="Error: run_id missing", actions=EventActions(error=True, escalate=True))
            return

        task_key = f"task:{run_id}:0"
        domain = ctx.session.state.get(task_key)

        if not domain:
            logger.error(f"Domain not found in session state for key: {task_key}")
            yield Event(author=self.name, content=f"Error: Domain missing for {task_key}", actions=EventActions(error=True, escalate=True))
            return

        logger.info(f"Simulating enrichment for domain: {domain}")
        # Simulate enrichment
        dummy_result = f"Successfully enriched data for {domain} (MVP simulation)"

        result_key = f"result:{run_id}:0"
        state_delta = {result_key: dummy_result}

        yield Event(
            author=self.name,
            content=types.Content(role=self.name, parts=[types.Part(text=f"Enrichment simulation complete for {domain}. Result: {dummy_result}")]),
            actions=EventActions(state_delta=state_delta)
        )


class CsvWriterAgent(BaseAgent):
    """Writes the original domain and enrichment result to the output CSV."""

    async def _run_async_impl(self, ctx: AgentContext) -> AsyncIterable[Event]:
        run_id = ctx.session.state.get("run_id")
        if not run_id:
            logger.error("run_id not found in session state for writing.")
            yield Event(author=self.name, content="Error: run_id missing for writer", actions=EventActions(error=True, escalate=True))
            return

        task_key = f"task:{run_id}:0"
        result_key = f"result:{run_id}:0"

        domain = ctx.session.state.get(task_key)
        enrichment_result = ctx.session.state.get(result_key)

        if domain is None or enrichment_result is None:
            logger.error(f"Missing domain or result for run_id '{run_id}' (task: {domain is not None}, result: {enrichment_result is not None})")
            yield Event(author=self.name, content=f"Error: Missing data for run {run_id}", actions=EventActions(error=True, escalate=True))
            return

        logger.info(f"Writing result for domain '{domain}' to: {OUTPUT_CSV}")
        try:
            # Ensure the output directory exists
            OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)

            # Check if file exists to decide whether to write header
            file_exists = OUTPUT_CSV.is_file()

            with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as outfile: # Use 'w' for MVP - overwrite each time
                fieldnames = [DOMAIN_COLUMN_HEADER, 'EnrichmentData']
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)

                # Write header only if file is new (or being overwritten in 'w' mode)
                # if not file_exists: # Not needed with 'w' mode
                writer.writeheader()

                writer.writerow({
                    DOMAIN_COLUMN_HEADER: domain,
                    'EnrichmentData': enrichment_result
                })

            logger.info(f"Successfully wrote enrichment data to {OUTPUT_CSV}")
            yield Event(
                author=self.name,
                content=types.Content(role=self.name, parts=[types.Part(text=f"Output written to {OUTPUT_CSV}")]),
                actions=EventActions(escalate=True) # Signal workflow completion
            )

        except Exception as e:
            logger.exception(f"Error writing CSV: {e}")
            yield Event(
                author=self.name,
                content=types.Content(role=self.name, parts=[types.Part(text=f"Error writing CSV: {e}")]),
                actions=EventActions(error=True, escalate=True)
            )


# Define the root agent for the MVP workflow
root_agent = SequentialAgent(
    name="enrichment_workflow",
    sub_agents=[
        CsvReaderAgent(name="csv_reader"),
        SimpleEnricherAgent(name="simple_enricher"),
        CsvWriterAgent(name="csv_writer")
    ]
)

# This makes the script runnable with `adk run .` from the workflow directory
# ADK automatically discovers the 'root_agent' variable.
