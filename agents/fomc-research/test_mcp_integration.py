#!/usr/bin/env python3
"""
Test script for MCP integration with FOMC Research Agent.

This script demonstrates how to initialize the agent with MCP tools
and run a simple test to verify the tools are properly loaded.
"""

import asyncio
import logging

from fomc_research.agent import initialize_agent_with_mcp, cleanup_mcp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Run a test of the MCP integration."""
    try:
        logger.info("Initializing agent with MCP tools...")
        agent = await initialize_agent_with_mcp()
        
        # Print out the available tools to verify MCP tools were loaded
        tool_names = [tool.name for tool in agent.tools]
        logger.info(f"Agent has {len(tool_names)} tools: {', '.join(tool_names)}")
        
        # You can add a test invocation here if desired
        # For example, if there's an MCP tool to list files:
        # response = await agent.invoke_tool("listFiles", {"path": "/"})
        # logger.info(f"MCP tool test response: {response}")
        
        logger.info("MCP integration test completed successfully")
    except Exception as e:
        logger.error(f"Error during MCP integration test: {e}")
    finally:
        # Always clean up MCP resources
        await cleanup_mcp()
        logger.info("Test completed, MCP resources cleaned up")

if __name__ == "__main__":
    asyncio.run(main())
