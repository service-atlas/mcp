from fastmcp import FastMCP

from api_calls import api_caller

teams_mcp = FastMCP("Teams MCP")


@teams_mcp.prompt('find_which_team_owns_a_service')
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


@teams_mcp.prompt('get_all_teams')
def prompt_get_all_teams() -> str:
    return """
        To get a list of all teams, use the tool `get_all_teams` or the resource `serviceatlas://teams`. The returned data will be an array of teams, which contains 
        an `id` field and a `name` field. The `id` field is the guid for the team, which will be used to make further calls.
    """


@teams_mcp.tool()
def get_all_teams():
    """
    Returns all teams from the service atlas api
    :return: array of teams objects
    """
    return _fetch_all_teams()


@teams_mcp.resource('serviceatlas://teams')
def get_all_teams_resource():
    """
    Returns all teams from the service atlas api
    :return: array of teams objects
    """
    return _fetch_all_teams()


@teams_mcp.tool()
def get_services_by_team(team_id: str):
    """
    Tool that returns a list of services for a team based on id
    :param team_id: guid for the team
    :return: array of services objects from the api
    """
    return api_caller.call_get(f'/teams/{team_id}/services')


@teams_mcp.resource('serviceatlas://teams/{team_id}/services')
def get_services_by_team_resource(team_id: str):
    """
    Resource that returns a list of services for a team based on id
    :param team_id: guid for the team
    :return: array of services objects from the api
    """
    return api_caller.call_get(f'/teams/{team_id}/services')


def _fetch_all_teams() -> list:
    """
    Returns all teams from the service atlas api.
    :return: list of teams objects (max of 200 due to pagination limit)
    """
    max_iterations = 10
    iteration = 0
    all_teams = []
    while iteration < max_iterations:
        iteration += 1
        teams = api_caller.call_get("/teams", params={"page": iteration, "pageSize": 20})
        if not teams:
            break
        all_teams.extend(teams)
    return all_teams
