"""People Finder sample agent."""

import logging
import warnings

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from . import MODEL, root_agent_prompt
from .shared_libraries.callbacks import rate_limit_callback
from .tools.store_state import store_state_tool as store_state_func
# from .tools.query_lemlist import query_lemlist_tool as query_lemlist_func
from .tools.save_contact_to_csv import save_contact_to_csv_tool as save_contact_func
from .tools.mcp import get_tools_async

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

logger = logging.getLogger(__name__)
logger.debug("Using MODEL: %s", MODEL)

async def create_agent():
    """Creates an agent with MCP tools loaded.
    
    Returns:
        tuple: (agent, exit_stack)
    """
    # Get MCP tools
    tools, exit_stack = await get_tools_async()
    
    # Create base tools list
    base_tools = [
        FunctionTool(func=store_state_func),
        # FunctionTool(func=query_lemlist_func)
        FunctionTool(func=save_contact_func),
    ]
    
    # Combine base tools with MCP tools
    all_tools = base_tools + list(tools)
    
    # Create agent with all tools
    agent = Agent(
        model=MODEL,
        name="root_agent",
        description=(
            "You are a prospecting assistant. Your job is to find as much as possible about a company based on their description."
        ),
        instruction=root_agent_prompt.PROMPT,
        tools=all_tools,
        before_model_callback=rate_limit_callback,
    )
    
    logger.info(f"Created agent with {len(all_tools)} tools ({len(tools)} MCP tools)")
    return agent, exit_stack

# Root agent is just the coroutine - ADK will await this when needed
root_agent = create_agent()
