#!/usr/bin/env python3
"""
Test script for MCP integration with FOMC Research Agent.

This script demonstrates how to initialize the agent with MCP tools
and run a simple test using the Runner to verify tool execution.
"""

import asyncio
import json
import logging

# ADK Core components
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# GenAI types for messages
from google.genai import types

# Local agent components
from fomc_research.agent import initialize_agent_with_mcp, cleanup_mcp


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Run a test of the MCP integration using the Runner."""
    agent = None # Define agent here to ensure it's in scope for finally block if init fails
    try:
        logger.info("Initializing agent with MCP tools...")
        agent = await initialize_agent_with_mcp()
        
        if not agent:
             logger.error("Agent initialization failed. Exiting test.")
             return # Exit if agent couldn't be created

        # Print out the available tools to verify MCP tools were loaded
        tool_names = [tool.name for tool in agent.tools]
        logger.info(f"Agent initialized with {len(tool_names)} tools: {', '.join(tool_names)}")
        
        # Check if the specific tool we want to test is loaded
        if "people_search" not in tool_names:
            logger.warning("'people_search' tool not found in agent's tools. Cannot test execution.")
            return # Exit if the tool isn't there

        # --- Setup Runner and Services ---
        logger.info("Setting up ADK Runner and services...")
        session_service = InMemorySessionService()
        artifacts_service = InMemoryArtifactService()
        session = session_service.create_session(
            state={}, app_name="fomc-research-test", user_id="test_user_01"
        )
        runner = Runner(
            app_name="fomc-research-test",
            agent=agent,
            artifact_service=artifacts_service,
            session_service=session_service,
        )

        # --- Define Aligned Test Query ---
        # This query aligns with the agent's prompt to find VPs of Sales using a domain.
        # Let's use the real domain as suggested for a more realistic test.
        question = "Find the sales people at elevenlabs.io" 
        logger.info(f"Test query: \"{question}\"")
        content = types.Content(role="user", parts=[types.Part(text=question)])

        # --- Run the Agent via Runner ---
        logger.info("Running agent via Runner...")
        events_async = runner.run_async(
            session_id=session.id, user_id="test_user_01", new_message=content
        )

        # --- Process Results ---
        logger.info("Processing execution events...")
        async for event in events_async:
            author = event.author
            if event.content:
                text_parts = [p.text for p in event.content.parts if p.text]
                if text_parts:
                     logger.info(f"[{author} - Text]: {' '.join(text_parts)}")

                function_calls = [p.function_call for p in event.content.parts if p.function_call]
                for fc in function_calls:
                    logger.info(f"[{author} - CALL]: {fc.name}({json.dumps(fc.args)})")
                    if fc.name == "people_search":
                        logger.info(">>> people_search tool was called.")

                function_responses = [p.function_response for p in event.content.parts if p.function_response]
                for fr in function_responses:
                    # --- FIX: Use str() for potentially non-JSON-serializable responses ---
                    try:
                        # Try json.dumps first for structured output if possible
                        response_content = json.dumps(fr.response)
                    except TypeError:
                        # Fallback to str() if json.dumps fails
                        response_content = str(fr.response) 
                        logger.warning(f"Response for {fr.name} could not be JSON serialized, using str(): {response_content}")

                    logger.info(f"[{author} - RESPONSE]: {fr.name} -> {response_content}")
                    if fr.name == "people_search":
                         logger.info(f">>> Response received for people_search.")
                         
            # Removed incorrect event.error check

        logger.info("Agent execution finished.")

    except Exception as e:
        logger.exception("Error during MCP integration test:") 
    finally:
        # Always clean up MCP resources
        logger.info("Cleaning up MCP resources...")
        await cleanup_mcp()
        logger.info("Test completed, MCP resources cleaned up.")

if __name__ == "__main__":
    asyncio.run(main())
