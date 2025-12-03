from fastmcp import FastMCP

from api_calls import api_caller

service_mcp = FastMCP("Service MCP")


@service_mcp.prompt('get_services_by_team')
def prompt_get_services_by_team(team_id: str) -> str:
    """
    Prompt for telling the AI how to get services if it has a team id
    :param team_id:
    :return:
    """
    return f"""
        To get a list of services for a team, use the resource: `serviceatlas://teams/{team_id}/services` 
        or the `get_services_by_team` tool, passing in a required 'teamId' parameter. It will return a list of services. 
        If you haven't previously called the 'get_teams' tool, you will need to do so you can get team Ids based on team names. This call expects a guid id passed in
    """


@service_mcp.prompt('find_service_by_name')
def prompt_get_service_by_name(query: str) -> str:
    """
    Prompt for telling the AI how to find a service by name
    :return:
    """
    return f"""
        To search for a service by name, use the tool `find_service_by_name`, passing in a required 'query' parameter, or 
        the resource `serviceatlas://services/search/{query}` with a query parameter.
    """


@service_mcp.tool()
def find_service_by_name(query: str):
    """
    Search for a service by name
    :param query: the name to search against
    :return: a list of services objects
    """
    return api_caller.call_get('/services/search', params={"query": query})


@service_mcp.resource('serviceatlas://services/search/{query}')
def find_service_by_name_resource(query: str):
    """
    Search for a service by name
    :param query: the name to search against
    :return: a list of services objects
    """
    return api_caller.call_get('/services/search', params={"query": query})


@service_mcp.tool()
def get_teams_by_service(service_id: str):
    """
    Gets a list of teams that own a service based on id
    :param service_id: the guid for the service
    :return: a list of teams objects
    """
    return api_caller.call_get(f'/services/{service_id}/teams')


@service_mcp.resource('serviceatlas://services/{service_id}/teams')
def get_teams_by_service_resource(service_id: str):
    """
    Gets a list of teams that own a service based on id
    :param service_id: the guid for the service
    :return: a list of teams objects
    """
    return api_caller.call_get(f'/services/{service_id}/teams')
