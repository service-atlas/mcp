import asyncio
import os
import sys

from fastmcp import FastMCP

from debt import debt_mcp
from services import service_mcp
from teams import teams_mcp

mcp = FastMCP("Service Map MCP")


def log(message: str):
    """Log a message to stderr to avoid interfering with STDIO transport."""
    sys.stderr.write(f"{message}\n")
    sys.stderr.flush()


async def setup():
    await mcp.import_server(debt_mcp)
    await mcp.import_server(teams_mcp)
    await mcp.import_server(service_mcp)


def main():
    """
    Main entry point for mcp service
    :return:
    """
    try:
        asyncio.run(setup())
        # Run the FastMCP server with STDIO transport
        mcp.run()
    except KeyboardInterrupt:
        log("Server shutdown requested by user")
    except Exception as e:
        log(f"Failed to start MCP Server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
