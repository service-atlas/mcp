import requests



def _fetch_services_by_team(team_id: str, api_url: str) -> list:
    """
    Calls the service atlas api to get services for a team
    :param team_id: the guid for the team
    :param api_url: the url base for the service atlas api
    :return:
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
    response = requests.get(f"{api_url}/teams", timeout=10)
    response.raise_for_status()
    return response.json()