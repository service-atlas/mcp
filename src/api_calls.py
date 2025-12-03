import os

import requests


class ApiCaller:
    def __init__(self):
        api_url = os.getenv("API_URL")
        if not api_url:
            api_url = "http://localhost:8080"
        self.__api_url = api_url

    def call_get(self, url: str, params: dict = None):
        """
        Calls the api with a get request
        :param url: the url fragment to append to the base url
        :param params: any query params to append to the url
        :return: json response
        """
        if not url.startswith("/"):
            url = f"/{url}"
        response = requests.get(f"{self.__api_url}{url}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()


api_caller = ApiCaller()
