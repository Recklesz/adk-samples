"""Initialization functions for FOMC Research Agent."""

from dotenv import load_dotenv
from pathlib import Path
import logging
import os

# Load .env from project root
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

loglevel = os.getenv("GOOGLE_GENAI_FOMC_AGENT_LOG_LEVEL", "INFO")
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError(f"Invalid log level: {loglevel}")
logger = logging.getLogger(__package__)
logger.setLevel(numeric_level)

MODEL = os.getenv("GOOGLE_GENAI_MODEL")
if not MODEL:
    MODEL = "gemini-2.5-flash-preview-04-17"

from . import agent  # pylint: disable=wrong-import-position
