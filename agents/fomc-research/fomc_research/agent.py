"""People Finder sample agent."""

import logging
import warnings

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from . import MODEL, root_agent_prompt
from .shared_libraries.callbacks import rate_limit_callback
from .tools.store_state import store_state_tool as store_state_func
from .tools.query_lemlist import query_lemlist_tool as query_lemlist_func

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

logger = logging.getLogger(__name__)
logger.debug("Using MODEL: %s", MODEL)


root_agent = Agent(
    model=MODEL,
    name="root_agent",
    description=(
        "You are a prospecting assistant. Your job is to find as much as possible about a company based on their description."
    ),
    instruction=root_agent_prompt.PROMPT,
    tools=[
        FunctionTool(func=store_state_func),
        FunctionTool(func=query_lemlist_func)
    ],
    before_model_callback=rate_limit_callback,
)
