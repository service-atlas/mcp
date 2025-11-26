import requests



def _fetch_services_by_team(team_id: str, api_url: str):
    response = requests.get(f"{api_url}/teams/{team_id}/services")
    response.raise_for_status()
    return response.json()
