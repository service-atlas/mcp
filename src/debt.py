from fastmcp import FastMCP

from api_calls import api_caller

debt_mcp = FastMCP("Debt MCP")


@debt_mcp.prompt('get_debt')
def prompt_get_debt() -> str:
    return """
        To get a list of all services and the count of all debts associated with them, use the tool `get_debt` or the resource `serviceatlas://debts`. 
        The returned data will be an array of objects with the format {name: <service name>, count: <number of debts>, id: <service id>}.
        If you wish to get a list of debts for a specific service, use the tool `get_debts_for_service` passing in the service id or the resource `serviceatlas://debts/{service_id}`.
    """


@debt_mcp.tool(annotations={"readOnlyHint": True, "title": "Get Debt Report"})
def get_debt():
    """
    Gets a report of all services that have open debts and a count of the number of debts associated with them
    :return:
    """
    return api_caller.call_get('/reports/services/debt')


@debt_mcp.resource(uri='serviceatlas://debts', name='Debt Report', mime_type='application/json')
def get_debts_resource():
    """
    Gets a report of all services that have open debts and a count of the number of debts associated with them
    :return:
    """
    return api_caller.call_get('/reports/services/debt')


@debt_mcp.tool(annotations={"readOnlyHint": True, "title": "Get Debts for Service"})
def get_debts_for_service(service_id: str):
    """
    Gets the debts for a specific service
    :param service_id:
    :return:
    """
    return api_caller.call_get(f'/services/{service_id}/debt')


@debt_mcp.resource(uri='serviceatlas://debts/{service_id}', name='Debts by Service', mime_type='application/json')
def get_debts_for_service_resource(service_id: str):
    """
    Gets the debts for a specific service
    :param service_id:
    :return:
    """
    return api_caller.call_get(f'/services/{service_id}/debt')


@debt_mcp.tool(annotations={"title": "Create Debt"})
def create_debt(service_id: str, title: str, description: str, type: str):
    """
    Creates a new debt item for a service
    :param service_id: The ID of the service
    :param title: The title of the debt
    :param description: A description of the debt
    :param type: The type of debt. Allowed values: 'code', 'documentation', 'testing', 'architecture', 'infrastructure', 'security'
    :return:
    """
    body = {
        "title": title,
        "description": description,
        "type": type,
        "status": "pending"
    }
    return api_caller.call_post(f'/services/{service_id}/debt', body=body)
