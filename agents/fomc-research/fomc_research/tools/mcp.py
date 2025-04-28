"""
MCP Tool integration for FOMC Research Agent.

This module provides an async loader for Model Context Protocol (MCP) tools,
connecting to a local MCP server (filesystem-backed) via stdio.

Usage:
    from .mcp import get_tools_async
    tools, exit_stack = await get_tools_async()

The MCP server must be running or startable via npx:
    npx -y @modelcontextprotocol/server-filesystem /Users/ivelinkozarev/PycharmProjects/ColdOutReachInfra/apollo-io-mcp-server
"""

from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

async def get_tools_async():
    """
    Starts the MCP server (filesystem) and loads the available tools.
    Returns:
        tools: List of tool definitions
        exit_stack: AsyncExitStack for context management
    """
    tools, exit_stack = await MCPToolset.from_server(
        connection_params=StdioServerParameters(
            command='npm',
            args=['run', 'stdio'],
            cwd='/Users/ivelinkozarev/PycharmProjects/ColdOutReachInfra/apollo-io-mcp-server'
        )
    )
    return tools, exit_stack
