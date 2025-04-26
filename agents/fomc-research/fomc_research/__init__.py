"""Initialization functions for FOMC Research Agent."""

import logging
import os

### TODO - this doesn't work - like the env stuff is not working here
loglevel = os.getenv("GOOGLE_GENAI_FOMC_AGENT_LOG_LEVEL", "DEBUG")
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError(f"Invalid log level: {loglevel}")
logger = logging.getLogger(__package__)
logger.setLevel(numeric_level)

MODEL = os.getenv("GOOGLE_GENAI_MODEL")
if not MODEL:
    MODEL = "gemini-2.5-flash-preview-04-17"

# MODEL needs to be defined before this import
from . import agent  # pylint: disable=wrong-import-position
