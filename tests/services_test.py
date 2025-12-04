import os
import sys
from typing import Any, List, Tuple

import pytest


# Ensure the 'src' directory is on sys.path so that modules like 'services' can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from importlib import import_module  # noqa: E402


def load_services_module():
    # Import lazily after sys.path modification so static analyzers don't fail
    return import_module("services")


class DummyApiCaller:
    def __init__(self, response: Any):
        self.response = response
        self.calls: List[Tuple[str, Any]] = []

    def call_get(self, url: str, params: dict | None = None):
        self.calls.append((url, params))
        return self.response


def test_prompt_get_services_by_team_mentions_tool_and_resource():
    services = load_services_module()
    prompt = services.prompt_get_services_by_team.fn("team-123")
    assert "get_services_by_team" in prompt
    assert "serviceatlas://teams/team-123/services" in prompt


def test_prompt_find_service_by_name_mentions_tool_and_resource():
    services = load_services_module()
    prompt = services.prompt_get_service_by_name.fn("orders")
    assert "find_service_by_name" in prompt
    assert "serviceatlas://services/search/orders" in prompt


def test_find_service_by_name_tool_calls_api_with_params_and_returns_data(
    monkeypatch: pytest.MonkeyPatch,
):
    services = load_services_module()
    fake_response = [
        {"id": "svc-1", "name": "orders"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    result = services.find_service_by_name.fn("orders")

    assert result == fake_response
    assert dummy.calls == [("/services/search", {"query": "orders"})]


def test_find_service_by_name_resource_calls_api_with_params_and_returns_data(
    monkeypatch: pytest.MonkeyPatch,
):
    services = load_services_module()
    fake_response = [
        {"id": "svc-2", "name": "billing"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    result = services.find_service_by_name_resource.fn("billing")

    assert result == fake_response
    assert dummy.calls == [("/services/search", {"query": "billing"})]


def test_get_teams_by_service_tool_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    services = load_services_module()
    fake_response = [
        {"id": "team-1", "name": "Team One"},
        {"id": "team-2", "name": "Team Two"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    result = services.get_teams_by_service.fn("svc-123")

    assert result == fake_response
    assert dummy.calls == [("/services/svc-123/teams", None)]


def test_get_teams_by_service_resource_calls_api_and_returns_data(
    monkeypatch: pytest.MonkeyPatch,
):
    services = load_services_module()
    fake_response = [
        {"id": "team-x", "name": "X"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    result = services.get_teams_by_service_resource.fn("svc-xyz")

    assert result == fake_response
    assert dummy.calls == [("/services/svc-xyz/teams", None)]
