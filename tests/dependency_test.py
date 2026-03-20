import os
import sys
from typing import Any, List, Tuple

import pytest


# Ensure the 'src' directory is on sys.path so that modules like 'dependency' can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from importlib import import_module  # noqa: E402


def load_dependency_module():
    # Import lazily after sys.path modification
    return import_module("dependency")


class DummyApiCaller:
    def __init__(self, response: Any):
        self.response = response
        self.calls: List[Tuple[str, Any]] = []

    def call_get(self, url: str, params: dict | None = None):
        self.calls.append((url, params))
        return self.response


def call_fn(func_or_tool, *args, **kwargs):
    if hasattr(func_or_tool, "fn"):
        return func_or_tool.fn(*args, **kwargs)
    return func_or_tool(*args, **kwargs)


def test_prompt_get_service_dependencies_and_dependents_mentions_tools_and_resources():
    dependency = load_dependency_module()
    prompt = call_fn(dependency.prompt_get_service_dependencies_and_dependents, "svc-123")
    assert "get_service_dependencies" in prompt
    assert "get_service_dependents" in prompt
    assert "serviceatlas://services/svc-123/dependencies" in prompt
    assert "serviceatlas://services/svc-123/dependents" in prompt


def test_get_service_dependencies_tool_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    dependency = load_dependency_module()
    fake_response = [
        {"id": "dep-1", "name": "Dependency One"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(dependency, "api_caller", dummy, raising=True)

    result = call_fn(dependency.get_service_dependencies, "svc-123")

    assert result == fake_response
    assert dummy.calls == [("/services/svc-123/dependencies", None)]


def test_get_service_dependencies_resource_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    dependency = load_dependency_module()
    fake_response = [
        {"id": "dep-2", "name": "Dependency Two"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(dependency, "api_caller", dummy, raising=True)

    result = call_fn(dependency.get_service_dependencies_resource, "svc-456")

    assert result == fake_response
    assert dummy.calls == [("/services/svc-456/dependencies", None)]


def test_get_service_dependents_tool_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    dependency = load_dependency_module()
    fake_response = [
        {"id": "dpt-1", "name": "Dependent One"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(dependency, "api_caller", dummy, raising=True)

    result = call_fn(dependency.get_service_dependents, "svc-123")

    assert result == fake_response
    assert dummy.calls == [("/services/svc-123/dependents", None)]


def test_get_service_dependents_resource_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    dependency = load_dependency_module()
    fake_response = [
        {"id": "dpt-2", "name": "Dependent Two"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(dependency, "api_caller", dummy, raising=True)

    result = call_fn(dependency.get_service_dependents_resource, "svc-456")

    assert result == fake_response
    assert dummy.calls == [("/services/svc-456/dependents", None)]
