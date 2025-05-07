"""CSV writer agent implementation."""

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
OUTPUT_CSV = Path(__file__).parent.parent.parent.parent / "output_mvp.csv"

class CsvWriterAgent(BaseAgent):
    """Writes enrichment results to output CSV."""
    async def _run_async_impl(self, ctx) -> AsyncIterable[Event]:
        enrichment = ctx.session.state.get("enrichment_result")
        if enrichment:
            logger.info(f"Writing enrichment result to: {OUTPUT_CSV}")
            try:
                with open(OUTPUT_CSV, mode='a', newline='', encoding='utf-8') as outfile:
                    writer = csv.writer(outfile)
                    writer.writerow([enrichment])
                yield Event(
                    author=self.name,
                    content=types.Content(role=self.name,
                                          parts=[types.Part(text=f"Result saved to {OUTPUT_CSV}")]),
                    actions=EventActions()
                )
            except Exception as e:
                logger.exception(f"Error writing CSV: {e}")
                yield Event(
                    author=self.name,
                    content=types.Content(role=self.name,
                                          parts=[types.Part(text=f"Error writing to CSV: {e}")]),
                    actions=EventActions()
                )
        else:
            yield Event(
                author=self.name,
                content=types.Content(role=self.name,
                                      parts=[types.Part(text="No enrichment result found to write.")]),
                actions=EventActions()
            )


# Create an instance of the agent
csv_writer_agent = CsvWriterAgent(name="csv_writer")
