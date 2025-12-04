import os
import sys
from typing import Any, Dict, List, Tuple

import pytest


# Ensure the 'src' directory is on sys.path so that modules like 'teams' can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from importlib import import_module  # noqa: E402


def load_teams_module():
    # Import lazily after sys.path modification so static analyzers don't fail
    return import_module("teams")


class DummyApiCaller:
    def __init__(self, response: Any):
        self.response = response
        self.calls: List[Tuple[str, Any]] = []

    def call_get(self, url: str, params: dict | None = None):
        self.calls.append((url, params))
        return self.response


class PagingDummyApiCaller:
    def __init__(self, pages: Dict[int, list]):
        self.pages = pages
        self.calls: List[Tuple[str, Any]] = []

    def call_get(self, url: str, params: dict | None = None):
        self.calls.append((url, params))
        if url == "/teams" and params and "page" in params:
            page = params["page"]
            return self.pages.get(page, [])
        return []


def test_prompt_find_which_team_owns_a_service_mentions_tools_and_resources():
    teams = load_teams_module()
    prompt = teams.prompt_find_which_team_owns_a_service.fn()
    assert "find_service_by_name" in prompt
    assert "get_teams_by_service" in prompt
    assert "serviceatlas://services/search/{query}" in prompt
    assert "serviceatlas://services/{service_id}/teams" in prompt


def test_prompt_get_all_teams_mentions_tool_and_resource():
    teams = load_teams_module()
    prompt = teams.prompt_get_all_teams.fn()
    assert "get_all_teams" in prompt
    assert "serviceatlas://teams" in prompt
    assert "id" in prompt and "name" in prompt


def test_get_all_teams_tool_paginates_and_aggregates(monkeypatch: pytest.MonkeyPatch):
    teams = load_teams_module()
    pages = {
        1: [{"id": "t1", "name": "Team One"}],
        2: [{"id": "t2", "name": "Team Two"}],
        # page 3 and beyond -> empty
    }
    dummy = PagingDummyApiCaller(pages)
    monkeypatch.setattr(teams, "api_caller", dummy, raising=True)

    result = teams.get_all_teams.fn()

    assert result == pages[1] + pages[2]
    # Expect three calls: pages 1, 2, then 3 (empty -> stop)
    assert dummy.calls == [
        ("/teams", {"page": 1, "pageSize": 20}),
        ("/teams", {"page": 2, "pageSize": 20}),
        ("/teams", {"page": 3, "pageSize": 20}),
    ]


def test_get_all_teams_resource_paginates_and_aggregates(monkeypatch: pytest.MonkeyPatch):
    teams = load_teams_module()
    pages = {
        1: [{"id": "a", "name": "Alpha"}],
        2: [{"id": "b", "name": "Beta"}],
    }
    dummy = PagingDummyApiCaller(pages)
    monkeypatch.setattr(teams, "api_caller", dummy, raising=True)

    result = teams.get_all_teams_resource.fn()

    assert result == pages[1] + pages[2]
    assert dummy.calls == [
        ("/teams", {"page": 1, "pageSize": 20}),
        ("/teams", {"page": 2, "pageSize": 20}),
        ("/teams", {"page": 3, "pageSize": 20}),
    ]


def test_get_services_by_team_tool_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    teams = load_teams_module()
    fake_response = [
        {"id": "svc-1", "name": "orders"},
        {"id": "svc-2", "name": "billing"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(teams, "api_caller", dummy, raising=True)

    result = teams.get_services_by_team.fn("team-123")

    assert result == fake_response
    assert dummy.calls == [("/teams/team-123/services", None)]


def test_get_services_by_team_resource_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    teams = load_teams_module()
    fake_response = [
        {"id": "svc-x", "name": "search"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(teams, "api_caller", dummy, raising=True)

    result = teams.get_services_by_team_resource.fn("my-team")

    assert result == fake_response
    assert dummy.calls == [("/teams/my-team/services", None)]
