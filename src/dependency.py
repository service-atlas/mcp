from fastmcp import FastMCP

from api_calls import api_caller

dependency_mcp = FastMCP("Dependency MCP")


@dependency_mcp.prompt('get_service_dependencies_and_dependents')
def prompt_get_service_dependencies_and_dependents(service_id: str) -> str:
    """
    Prompt for telling the AI how to get a service's dependencies and dependents
    :param service_id:
    :return:
    """
    return f"""
        To get a list of dependencies for a service, use the resource: `serviceatlas://services/{service_id}/dependencies` 
        or the `get_service_dependencies` tool, passing in a required 'service_id' parameter. It will return a list of dependencies. 
        
        To get a list of dependents for a service, use the resource: `serviceatlas://services/{service_id}/dependents` 
        or the `get_service_dependents` tool, passing in a required 'service_id' parameter. It will return a list of dependents. 
    """


@dependency_mcp.tool(annotations={"readOnlyHint": True, "title": "Get Service Dependencies"})
def get_service_dependencies(service_id: str):
    """
    Gets a list of services that this service depends on
    :param service_id: the guid for the service
    :return: a list of dependency objects
    """
    return api_caller.call_get(f'/services/{service_id}/dependencies')


@dependency_mcp.resource(uri='serviceatlas://services/{service_id}/dependencies', name='Service Dependencies', mime_type='application/json')
def get_service_dependencies_resource(service_id: str):
    """
    Gets a list of services that this service depends on
    :param service_id: the guid for the service
    :return: a list of dependency objects
    """
    return api_caller.call_get(f'/services/{service_id}/dependencies')


@dependency_mcp.tool(annotations={"readOnlyHint": True, "title": "Get Service Dependents"})
def get_service_dependents(service_id: str):
    """
    Gets a list of services that depend on this service
    :param service_id: the guid for the service
    :return: a list of dependent objects
    """
    return api_caller.call_get(f'/services/{service_id}/dependents')


@dependency_mcp.resource(uri='serviceatlas://services/{service_id}/dependents', name='Service Dependents', mime_type='application/json')
def get_service_dependents_resource(service_id: str):
    """
    Gets a list of services that depend on this service
    :param service_id: the guid for the service
    :return: a list of dependent objects
    """
    return api_caller.call_get(f'/services/{service_id}/dependents')

