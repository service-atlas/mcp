import requests



def _fetch_services_by_team(api_url: str, team_id: str) -> list:
    """
    Calls the service atlas api to get services for a team
    :param api_url: the url base for the service atlas api
    :param team_id: the guid for the team
    :return: a list of service objects a team owns
    """
    response = requests.get(f"{api_url}/teams/{team_id}/services", timeout=10)
    response.raise_for_status()
    return response.json()

def _fetch_all_teams(api_url: str) -> list:
    """
    Returns all teams from the service atlas api
    :param api_url: the url base for the service atlas api
    :return:
    """
    response = requests.get(f"{api_url}/teams", params={"page": 1, "pageSize": 20}, timeout=10)
    response.raise_for_status()
    return response.json()

def _search_service_by_name(api_url: str, query: str) -> list:
    """
    Does a fuzzy search for a service by name
    :param api_url: the base url for the service atlas api
    :param query: the name of the service to search on
    :return: a list of service objects
    """
    response = requests.get(f"{api_url}/services/search", params={"query":query}, timeout=10)
    response.raise_for_status()
    return response.json()

def _fetch_teams_by_service_id(api_url: str, service_id: str) -> list:
    """
    Returns all teams that own a service
    :param api_url: the base url for the service atlas api
    :param service_id: the guid for the service
    :return: a list of team objects
    """
    response = requests.get(f"{api_url}/services/{service_id}/teams", timeout=10)
    response.raise_for_status()
    return response.json()