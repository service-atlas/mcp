from fastmcp import FastMCP

from api_calls import api_caller

release_mcp = FastMCP("Releases MCP")


@release_mcp.prompt('get_releases')
def prompt_get_releases(start: str, end: str) -> str:
    """
    Get a list of releases between two dates
    :param start: start date in the format YYYY-MM-DD
    :param end: end date in the format YYYY-MM-DD
    :return: string prompt
    """
    return f"""
        To get a list of all releases between two dates, use the tool `get_releases` or the resource `serviceatlas://releases/{start}/{end}`.
        If you wish to search for releases today, the end date will need to have a value of tomorrow. The return object will be 
        an array of release objects, with a service name, service id, version, and release date.
    """


@release_mcp.resource(uri='serviceatlas://releases/{start}/{end}', name='Get Releases in Date Range', mime_type='application/json')
def get_releases_resource(start: str, end: str) -> list:
    """
    Get a list of releases between two dates. Start date is inclusive, while the end date is an exclusive
    :param start: start date in the format YYYY-MM-DD (inclusive)
    :param end: end date in the format YYYY-MM-DD (exclusive)
    :return: list of releases
    """
    return api_caller.call_get(f'/releases/{start}/{end}')


@release_mcp.tool(annotations={'readOnlyHint': True, 'title': 'Get Releases in Date Range'})
def get_releases(start: str, end: str) -> list:
    """
    Get a list of releases between two dates. Start date is inclusive, while the end date is an exclusive
    :param start: start date in the format YYYY-MM-DD (inclusive)
    :param end: end date in the format YYYY-MM-DD (exclusive)
    :return: list of releases
    """
    return api_caller.call_get(f'/releases/{start}/{end}')
