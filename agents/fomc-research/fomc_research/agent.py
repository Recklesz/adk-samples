"""People Finder sample agent."""

import logging
import warnings

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from . import MODEL, root_agent_prompt
from .shared_libraries.callbacks import rate_limit_callback
from .tools.store_state import store_state_tool as store_state_func
# from .tools.query_lemlist import query_lemlist_tool as query_lemlist_func
from .tools.mcp import get_tools_async

warnings.filterwarnings("ignore", category=UserWarning, module=".*pydantic.*")

logger = logging.getLogger(__name__)
logger.debug("Using MODEL: %s", MODEL)


# Default agent configuration without MCP tools
root_agent = Agent(
    model=MODEL,
    name="root_agent",
    description=(
        "You are a prospecting assistant. Your job is to find as much as possible about a company based on their description."
    ),
    instruction=root_agent_prompt.PROMPT,
    tools=[
        FunctionTool(func=store_state_func),
        # FunctionTool(func=query_lemlist_func)
    ],
    before_model_callback=rate_limit_callback,
)

# Exit stack for MCP server context management
_mcp_exit_stack = None

async def initialize_agent_with_mcp():
    """Initialize the agent with MCP tools loaded asynchronously.
    
    Returns:
        Agent: The configured agent with MCP tools added
    """
    global _mcp_exit_stack
    
    # First, load MCP tools
    try:
        mcp_tools, exit_stack = await get_tools_async()
        _mcp_exit_stack = exit_stack  # Store for cleanup later
        logger.info(f"Loaded {len(mcp_tools)} MCP tools")
        
        # Create a new agent with both standard and MCP tools
        base_tools = [
            FunctionTool(func=store_state_func),
            # FunctionTool(func=query_lemlist_func)
        ]
        
        # Combine base tools with MCP tools
        all_tools = base_tools + list(mcp_tools)
        
        # Create the agent with all tools included
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
        
        logger.info(f"Created agent with {len(all_tools)} tools ({len(mcp_tools)} MCP tools)")
        return agent
    except Exception as e:
        logger.error(f"Failed to initialize MCP tools: {e}")
        
        # Fallback to standard agent without MCP tools
        logger.info("Falling back to standard agent without MCP tools")
        return Agent(
            model=MODEL,
            name="root_agent",
            description=(
                "You are a prospecting assistant. Your job is to find as much as possible about a company based on their description."
            ),
            instruction=root_agent_prompt.PROMPT,
            tools=[
                FunctionTool(func=store_state_func),
                # FunctionTool(func=query_lemlist_func)
            ],
            before_model_callback=rate_limit_callback,
        )

async def cleanup_mcp():
    """Clean up MCP resources when done."""
    global _mcp_exit_stack
    if _mcp_exit_stack:
        await _mcp_exit_stack.aclose()
        _mcp_exit_stack = None
        logger.info("MCP resources cleaned up")
