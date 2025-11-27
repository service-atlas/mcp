import requests



def _fetch_services_by_team(team_id: str, api_url: str):
    """
    Calls the service atlas api to get services for a team
    :param team_id:
    :param api_url:
    :return:
    """
    response = requests.get(f"{api_url}/teams/{team_id}/services")
    response.raise_for_status()
    return response.json()

def _fetch_all_teams(api_url: str) -> list:
    """
    Returns all teams from the service atlas api
    :param api_url:
    :return:
    """
    response = requests.get(f"{api_url}/teams")
    response.raise_for_status()
    return response.json()