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


@service_mcp.prompt('get_service_risk')
def prompt_get_service_risk(service_id: str) -> str:
    """
    Prompt for telling the AI how to get a service's risk report
    :param service_id:
    :return:
    """
    return f"""
        To get the risk report for a service, use the tool `get_service_risk` or the resource `serviceatlas://services/{service_id}/risk`. 
        The report includes change risk (heuristic signal for cascading impact) and health risk (debt and dependent counts).
    """


@service_mcp.tool(annotations={"readOnlyHint": True, "title": "Find Service by Name"})
def find_service_by_name(query: str):
    """
    Search for a service by name
    :param query: the name to search against
    :return: a list of services objects
    """
    return api_caller.call_get('/services/search', params={"query": query})


@service_mcp.resource(uri='serviceatlas://services/search/{query}', name='Search Services by Name', mime_type='application/json')
def find_service_by_name_resource(query: str):
    """
    Search for a service by name
    :param query: the name to search against
    :return: a list of services objects
    """
    return api_caller.call_get('/services/search', params={"query": query})


@service_mcp.tool(annotations={"readOnlyHint": True, "title": "Get Teams for Service"})
def get_teams_by_service(service_id: str):
    """
    Gets a list of teams that own a service based on id
    :param service_id: the guid for the service
    :return: a list of teams objects
    """
    return api_caller.call_get(f'/services/{service_id}/teams')


@service_mcp.resource(uri='serviceatlas://services/{service_id}/teams', name='Teams by Service', mime_type='application/json')
def get_teams_by_service_resource(service_id: str):
    """
    Gets a list of teams that own a service based on id
    :param service_id: the guid for the service
    :return: a list of teams objects
    """
    return api_caller.call_get(f'/services/{service_id}/teams')


@service_mcp.tool(annotations={"readOnlyHint": True, "title": "Get Service Risk Report"})
def get_service_risk(service_id: str):
    """
    Gets the risk report for a specific service
    :param service_id: the guid for the service
    :return: risk report object
    """
    return api_caller.call_get(f'/reports/services/{service_id}/risk')


@service_mcp.resource(uri='serviceatlas://services/{service_id}/risk', name='Service Risk Report', mime_type='application/json')
def get_service_risk_resource(service_id: str):
    """
    Gets the risk report for a specific service
    :param service_id: the guid for the service
    :return: risk report object
    """
    return api_caller.call_get(f'/reports/services/{service_id}/risk')

@service_mcp.resource(uri='serviceatlas://services/types', name='Get Service Types', mime_type='application/json')
def get_service_types_resource():
    """
    Gets the list of service types
    :return: list of service types
    """
    return api_caller.call_get('/services/types')

@service_mcp.tool(annotations={"readOnlyHint": True, "title": "Get Service Types"})
def get_service_types():
    """
    Gets the list of service types
    :return: list of service types
    """
    return api_caller.call_get('/services/types')

@service_mcp.tool(annotations={"readOnlyHint": False, "title": "Create Service"})
def create_service(name: str, description: str = "", type: str = "service", url: str = None, tier: int = 3):
    """
    Creates a new service
    :param name: name of the service
    :param description: optional description of the service
    :param type: type of the service (defaults to "service"). Type should be expressly asked for by the user
    :param url: optional url for the service
    :param tier: optional tier for the service (1=Mission Critical, 2=Business Critical, 3=Supporting, 4=Non-Critical/Auxiliary, defaults to 3)
    :return: the created service object
    """
    body = {
        "name": name,
        "description": description,
        "type": type,
        "tier": tier
    }
    if url:
        body["url"] = url
    return api_caller.call_post("/services", body=body)

@service_mcp.tool(annotations={"readOnlyHint": False, "title": "Update Service"})
def update_service(service_id: str, name: str, description: str = "", type: str = "service", url: str = None, tier: int = 3):
    """
    Updates an existing service. It is recommended to get the service first and then update it, so all fields are updated.
    :param service_id: id of the service to update
    :param name:  the name of the service. WARNING: Changing the name is discouraged as it may break references in code, configs, and dependencies.
        Only update the name if explicitly and intentionally requested by the user — do not infer or suggest name changes.
    :param description: optional description of the service
    :param type: type of the service (defaults to "service"). WARNING: Changing the type is discouraged as it may have downstream impacts.
        Only update if explicitly and intentionally requested by the user — do not infer or suggest type changes.
    :param url: optional url for the service
    :param tier: optional tier for the service (1=Mission Critical, 2=Business Critical, 3=Supporting, 4=Non-Critical/Auxiliary, defaults to 3)
    :return: the created service object
    """
    body = {
        "id": service_id,
        "name": name,
        "description": description,
        "type": type,
        "tier": tier
    }
    if url:
        body["url"] = url
    return api_caller.call_put(f"/services/{service_id}", body=body)