from fastmcp import FastMCP
from fastmcp.server.transforms import ResourcesAsTools
from api_calls import api_caller

dependency_mcp = FastMCP("Dependency MCP")

dependency_mcp.add_transform(ResourcesAsTools(dependency_mcp))

@dependency_mcp.prompt('get_service_dependencies_and_dependents')
def prompt_get_service_dependencies_and_dependents(service_id: str) -> str:
    """
    Prompt for telling the AI how to get a service's dependencies and dependents
    :param service_id:
    :return:
    """
    return f"""
        To get a list of dependencies for a service, use the resource: `serviceatlas://services/{service_id}/dependencies`. It will return a list of dependencies. 
        
        To get a list of dependents for a service, use the resource: `serviceatlas://services/{service_id}/dependents`. It will return a list of dependents. 
        
        To create a dependency connection between two entities, use the tool: `create_dependency`, passing in the 'service_id' (service that depends), 'dependency_id' (service it depends on), and optionally 'version' and 'interaction_type'.
        
        'interaction_type' can be one of:
        - 'data' (default): A direct, synchronous exchange of meaningful domain data between two services. Represents logical data flow.
        - 'security': A dependency on a service that handles authentication, authorisation, or request routing.
        - 'performance': A dependency on a service that exists to optimise speed or reduce load.
        - 'async': A dependency where the interaction is fire-and-forget or event-driven.
        - 'config': A dependency on a service that provides configuration, feature flags, or secrets at runtime.
    """




@dependency_mcp.tool()
def create_dependency(service_id: str, dependency_id: str, version: str = None, interaction_type: str = None):
    """
    Creates a dependency connection between two entities.
    The service_id will depend on the dependency_id. The service_id is the consumer/caller that relies on dependency_id
    If it is not clear what which service depends on which, ask clarifying questions.
    :param service_id: the guid for the service that will depend on the other service
    :param dependency_id: the guid for the service that is being depended on
    :param version: the version of the dependency
    :param interaction_type: the type of interaction (data, security, performance, async, config)
    :return: json response
    """
    if not service_id or not dependency_id:
        raise ValueError("service_id and dependency_id are required")
    if service_id == dependency_id:
        raise ValueError("A service cannot depend on itself")
    body = {"id": dependency_id}
    if version:
        body["version"] = version
    if interaction_type:
        body["interaction_type"] = interaction_type
    response = api_caller.call_post(f'/services/{service_id}/dependency', body=body)
    return response if response else '{"status": "success"}'

@dependency_mcp.tool(annotations={"readOnlyHint": True, "title": "Remove Dependency"})
def remove_dependency():
    """
    NOTE TO AI: Removing a dependency is a sensitive action that is intentionally not
    available via this API. If the user requests this, call get_website to retrieve
    the URL, then inform the user they must remove dependencies manually through their
    Service Atlas web interface. If get_website returns an error, tell the user to
    visit their Service Atlas web interface without providing a specific URL.
    """
    pass

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