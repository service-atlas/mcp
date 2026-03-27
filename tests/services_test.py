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
        self.calls.append(("GET", url, params))
        return self.response

    def call_post(self, url: str, body: dict | None = None):
        self.calls.append(("POST", url, body))
        return self.response


def call_fn(func_or_tool, *args, **kwargs):
    if hasattr(func_or_tool, "fn"):
        return func_or_tool.fn(*args, **kwargs)
    return func_or_tool(*args, **kwargs)


def test_prompt_get_services_by_team_mentions_tool_and_resource():
    services = load_services_module()
    prompt = call_fn(services.prompt_get_services_by_team, "team-123")
    assert "get_services_by_team" in prompt
    assert "serviceatlas://teams/team-123/services" in prompt


def test_prompt_find_service_by_name_mentions_tool_and_resource():
    services = load_services_module()
    prompt = call_fn(services.prompt_get_service_by_name, "orders")
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

    result = call_fn(services.find_service_by_name, "orders")

    assert result == fake_response
    assert dummy.calls == [("GET", "/services/search", {"query": "orders"})]


def test_find_service_by_name_resource_calls_api_with_params_and_returns_data(
    monkeypatch: pytest.MonkeyPatch,
):
    services = load_services_module()
    fake_response = [
        {"id": "svc-2", "name": "billing"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    result = call_fn(services.find_service_by_name_resource, "billing")

    assert result == fake_response
    assert dummy.calls == [("GET", "/services/search", {"query": "billing"})]


def test_get_teams_by_service_tool_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    services = load_services_module()
    fake_response = [
        {"id": "team-1", "name": "Team One"},
        {"id": "team-2", "name": "Team Two"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    result = call_fn(services.get_teams_by_service, "svc-123")

    assert result == fake_response
    assert dummy.calls == [("GET", "/services/svc-123/teams", None)]


def test_get_teams_by_service_resource_calls_api_and_returns_data(
    monkeypatch: pytest.MonkeyPatch,
):
    services = load_services_module()
    fake_response = [
        {"id": "team-x", "name": "X"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    result = call_fn(services.get_teams_by_service_resource, "svc-xyz")

    assert result == fake_response
    assert dummy.calls == [("GET", "/services/svc-xyz/teams", None)]


def test_prompt_get_service_risk_mentions_tool_and_resource():
    services = load_services_module()
    prompt = call_fn(services.prompt_get_service_risk, "svc-123")
    assert "get_service_risk" in prompt
    assert "serviceatlas://services/svc-123/risk" in prompt


def test_get_service_risk_tool_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    services = load_services_module()
    fake_response = {
        "changeRisk": {"risk": "medium", "score": 60},
        "healthRisk": {"debtCount": {"code": 1, "documentation": 1}, "dependentCount": 1},
    }
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    result = call_fn(services.get_service_risk, "svc-123")

    assert result == fake_response
    assert dummy.calls == [("GET", "/reports/services/svc-123/risk", None)]


def test_get_service_risk_resource_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    services = load_services_module()
    fake_response = {
        "changeRisk": {"risk": "low", "score": 20},
    }
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    result = call_fn(services.get_service_risk_resource, "svc-456")

    assert result == fake_response
    assert dummy.calls == [("GET", "/reports/services/svc-456/risk", None)]


def test_create_service_tool_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    services = load_services_module()
    fake_response = {
        "id": "new-svc-id",
        "name": "NewService",
        "type": "service",
        "description": "Description",
        "tier": 2,
        "url": "http://example.com"
    }
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    result = call_fn(
        services.create_service,
        name="NewService",
        description="Description",
        tier=2,
        url="http://example.com"
    )

    assert result == fake_response
    assert dummy.calls == [
        (
            "POST",
            "/services",
            {
                "name": "NewService",
                "description": "Description",
                "type": "service",
                "tier": 2,
                "url": "http://example.com"
            }
        )
    ]


def test_create_service_tool_uses_defaults(monkeypatch: pytest.MonkeyPatch):
    services = load_services_module()
    fake_response = {"id": "new-svc-id"}
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    call_fn(services.create_service, name="Svc", description="Desc")

    assert dummy.calls == [
        (
            "POST",
            "/services",
            {
                "name": "Svc",
                "description": "Desc",
                "type": "service",
                "tier": 3
            }
        )
    ]


def test_get_service_types_tool_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    services = load_services_module()
    fake_response = ["service", "library", "resource", "internal"]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    result = call_fn(services.get_service_types)

    assert result == fake_response
    assert dummy.calls == [("GET", "/services/types", None)]


def test_get_service_types_resource_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    services = load_services_module()
    fake_response = ["service", "library", "resource", "internal"]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(services, "api_caller", dummy, raising=True)

    result = call_fn(services.get_service_types_resource)

    assert result == fake_response
    assert dummy.calls == [("GET", "/services/types", None)]
