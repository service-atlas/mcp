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


@debt_mcp.tool()
def get_debt():
    return api_caller.call_get('/reports/services/debt')


@debt_mcp.resource(uri='serviceatlas://debts', name='Get Debt Report', mime_type='application/json')
def get_debts_resource():
    return api_caller.call_get('/reports/services/debt')


@debt_mcp.tool()
def get_debts_for_service(service_id: str):
    return api_caller.call_get(f'/services/{service_id}/debt')


@debt_mcp.resource('serviceatlas://debts/{service_id}')
def get_debts_for_service_resource(service_id: str):
    return api_caller.call_get(f'/services/{service_id}/debt')
