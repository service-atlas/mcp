from fastmcp import FastMCP
import os
import sys


mcp = FastMCP("Service Map MCP")

def log(message: str):
    """Log message to stderr to avoid interfering with STDIO transport."""
    sys.stderr.write(f"{message}\n")
    sys.stderr.flush()





def main():
    """
    Main entry point for mcp service
    :return:
    """
    try:
        api_url = os.getenv("API_URL")
        if not api_url:
            raise ValueError("API_URL environment variable is required.")
        # Run the FastMCP server with STDIO transport
        mcp.run()
    except KeyboardInterrupt:
        log("Server shutdown requested by user")
    except Exception as e:
        log(f"Failed to start Stock MCP Server: {e}")
        sys.exit(1)
