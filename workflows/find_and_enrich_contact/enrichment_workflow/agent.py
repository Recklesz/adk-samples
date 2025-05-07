import logging

from google.adk.agents import SequentialAgent

# Import sub-agents
from .sub_agents.simple_enricher import simple_enricher_agent
from .sub_agents.csv_writer import csv_writer_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the root agent with the sub-agents
root_agent = SequentialAgent(
    name="root",
    description=(
        'Enriches company data by processing domains from a CSV file and writing'
        ' the enriched data back to an output CSV file.'
    ),
    sub_agents=[simple_enricher_agent, csv_writer_agent],
)
