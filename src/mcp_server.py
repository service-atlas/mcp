import asyncio

from fastmcp import FastMCP
import os
import sys
from api_calls import (
    _fetch_services_by_team,
    _search_service_by_name,
    _fetch_teams_by_service_id,
    _fetch_all_teams)

from debt import debt_mcp

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
        To get a list of services for a team, use the resource: serviceatlas://teams/{team_id}/services` 
        or the `get_services_by_team` tool, passing in a required 'teamId' parameter. It will return a list of services. 
        If you haven't previously called the 'get_teams' tool, you will need to do so you can get team Ids based on team names. This call expects a guid id passed in
    """


@mcp.prompt('find_service_by_name')
def prompt_get_service_by_name(query: str) -> str:
    """
    Prompt for telling the AI how to find a service by name
    :return:
    """
    return f"""
        To search for a service by name, use the tool `find_service_by_name`, passing in a required 'query' parameter, or 
        the resource `serviceatlas://services/search/{query}` with a query parameter.
    """


@mcp.prompt('find_which_team_owns_a_service')
def prompt_find_which_team_owns_a_service() -> str:
    """
    Prompt for telling the AI how to find which team owns a service
    :return:
    """
    return """
        To find which team owns a service, first use the tool `find_service_by_name` to find the service you are interested in (if you haven't already).
        The returned data will have an `id` field. You will then need to call the tool `get_teams_by_service` passing in the service id.
        There are also associated resources for each tool. The `serviceatlas://services/search/{query}` resource is synonymous with the `find_service_by_name` tool.
        The `serviceatlas://services/{service_id}/teams` resource is synonymous with the `get_teams_by_service` tool.
        """


@mcp.prompt('get_all_teams')
def prompt_get_all_teams() -> str:
    return """
        To get a list of all teams, use the tool `get_all_teams` or the resource `serviceatlas://teams`. The returned data will be an array of teams, which contains 
        an `id` field and a `name` field. The `id` field is the guid for the team, which will be used to make further calls.
    """



@mcp.tool()
def find_service_by_name(query: str):
    """
    Search for a service by name
    :param query: the name to search against
    :return: a list of services objects
    """
    return _search_service_by_name(api_url, query)


@mcp.resource('serviceatlas://services/search/{query}')
def find_service_by_name_resource(query: str):
    """
    Search for a service by name
    :param query: the name to search against
    :return: a list of services objects
    """
    return _search_service_by_name(api_url, query)


@mcp.tool()
def get_teams_by_service(service_id: str):
    """
    Gets a list of teams that own a service based on id
    :param service_id: the guid for the service
    :return: a list of teams objects
    """
    return _fetch_teams_by_service_id(api_url, service_id)


@mcp.resource('serviceatlas://services/{service_id}/teams')
def get_teams_by_service_resource(service_id: str):
    """
    Gets a list of teams that own a service based on id
    :param service_id: the guid for the service
    :return: a list of teams objects
    """
    return _fetch_teams_by_service_id(api_url, service_id)


@mcp.tool()
def get_services_by_team(team_id: str):
    """
    Tool that returns a list of services for a team based on id
    :param team_id: guid for the team
    :return: array of services objects from the api
    """
    return _fetch_services_by_team(api_url, team_id)


@mcp.resource('serviceatlas://teams/{team_id}/services')
def get_services_by_team_resource(team_id: str):
    """
    Resource that returns a list of services for a team based on id
    :param team_id: guid for the team
    :return: array of services objects from the api
    """
    return _fetch_services_by_team(api_url, team_id)


@mcp.tool()
def get_all_teams():
    """
    Returns all teams from the service atlas api
    :return: array of teams objects
    """
    return _fetch_all_teams(api_url)


@mcp.resource('serviceatlas://teams')
def get_all_teams_resource():
    """
    Returns all teams from the service atlas api
    :return: array of teams objects
    """
    return _fetch_all_teams(api_url)


async def setup():
    await mcp.import_server(debt_mcp)


def main():
    """
    Main entry point for mcp service
    :return:
    """
    try:
        global api_url
        api_url = os.getenv("API_URL")
        if not api_url:
            api_url = "http://localhost:8080"
            # raise ValueError("API_URL environment variable is required.")
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
