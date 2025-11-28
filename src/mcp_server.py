from fastmcp import FastMCP
import os
import sys
from get_services_by_team import _fetch_services_by_team

api_url = ""

mcp = FastMCP("Service Map MCP")

def log(message: str):
    """Log a message to stderr to avoid interfering with STDIO transport."""
    sys.stderr.write(f"{message}\n")
    sys.stderr.flush()

@mcp.prompt('get_services_by_team')
def prompt_get_services_by_team(team_id: str) -> str:
    """
    Prompt for telling the AI how to get services if it has a team id
    :param team_id:
    :return:
    """
    return f"""
        To get a list of services for a team, use the resource: servicemap://teams/{team_id}/services` 
        or the `get_services_by_team` tool, passing in a required 'teamId' parameter. It will return a list of services. 
        If you haven't previously called the 'get_teams' tool, you will need to do so you can get team Ids based on team names. This call expects a guid id passed in
    """

@mcp.tool()
def get_services_by_team(team_id: str):
    """
    Tool that returns a list of services for a team based on id
    :param team_id: guid for the team
    :return: array of services objects from the api
    """
    return _fetch_services_by_team(team_id, api_url)

@mcp.resource('servicemap://teams/{team_id}/services')
def get_services_by_team_resource(team_id: str):
    """
    Resource that returns a list of services for a team based on id
    :param team_id: guid for the team
    :return: array of services objects from the api
    """
    return _fetch_services_by_team(team_id, api_url)


def main():
    """
    Main entry point for mcp service
    :return:
    """
    try:
        global api_url
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


if __name__ == "__main__":
    main()