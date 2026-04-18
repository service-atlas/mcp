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
        self.calls.append(("GET", url, params))
        return self.response

    def call_post(self, url: str, body: dict | None = None):
        self.calls.append(("POST", url, body))
        return self.response


def call_fn(func_or_tool, *args, **kwargs):
    if hasattr(func_or_tool, "fn"):
        return func_or_tool.fn(*args, **kwargs)
    return func_or_tool(*args, **kwargs)


def test_prompt_get_service_dependencies_and_dependents_mentions_tools_and_resources():
    dependency = load_dependency_module()
    prompt = call_fn(dependency.prompt_get_service_dependencies_and_dependents, "svc-123")
    assert "serviceatlas://services/svc-123/dependencies" in prompt
    assert "serviceatlas://services/svc-123/dependents" in prompt
    assert "interaction_type" in prompt
    assert "data" in prompt
    assert "security" in prompt
    assert "performance" in prompt
    assert "async" in prompt
    assert "config" in prompt


def test_get_service_dependencies_resource_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    dependency = load_dependency_module()
    fake_response = [
        {"id": "dep-2", "name": "Dependency Two"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(dependency, "api_caller", dummy, raising=True)

    result = call_fn(dependency.get_service_dependencies_resource, "svc-456")

    assert result == fake_response
    assert dummy.calls == [("GET", "/services/svc-456/dependencies", None)]


def test_get_service_dependents_resource_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    dependency = load_dependency_module()
    fake_response = [
        {"id": "dpt-2", "name": "Dependent Two"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(dependency, "api_caller", dummy, raising=True)

    result = call_fn(dependency.get_service_dependents_resource, "svc-456")

    assert result == fake_response
    assert dummy.calls == [("GET", "/services/svc-456/dependents", None)]


def test_create_dependency_tool_calls_api_with_post(monkeypatch: pytest.MonkeyPatch):
    dependency = load_dependency_module()
    fake_response = None
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(dependency, "api_caller", dummy, raising=True)

    result = call_fn(dependency.create_dependency, service_id="svc-1", dependency_id="svc-2", version="1.0.0")

    assert result == '{"status": "success"}'
    assert dummy.calls == [("POST", "/services/svc-1/dependency", {"id": "svc-2", "version": "1.0.0"})]


def test_create_dependency_tool_calls_api_with_interaction_type(monkeypatch: pytest.MonkeyPatch):
    dependency = load_dependency_module()
    fake_response = None
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(dependency, "api_caller", dummy, raising=True)

    result = call_fn(dependency.create_dependency, service_id="svc-1", dependency_id="svc-2", interaction_type="security")

    assert result == '{"status": "success"}'
    assert dummy.calls == [("POST", "/services/svc-1/dependency", {"id": "svc-2", "interaction_type": "security"})]


def test_create_dependency_tool_calls_api_with_version_and_interaction_type(monkeypatch: pytest.MonkeyPatch):
    dependency = load_dependency_module()
    fake_response = None
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(dependency, "api_caller", dummy, raising=True)

    result = call_fn(dependency.create_dependency, service_id="svc-1", dependency_id="svc-2", version="1.5.0", interaction_type="data")

    assert result == '{"status": "success"}'
    assert dummy.calls == [("POST", "/services/svc-1/dependency", {"id": "svc-2", "version": "1.5.0", "interaction_type": "data"})]


def test_create_dependency_tool_no_content_returns_success_string(monkeypatch: pytest.MonkeyPatch):
    dependency = load_dependency_module()
    fake_response = None
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(dependency, "api_caller", dummy, raising=True)

    result = call_fn(dependency.create_dependency, service_id="svc-1", dependency_id="svc-2")

    assert result == '{"status": "success"}'
    assert dummy.calls == [("POST", "/services/svc-1/dependency", {"id": "svc-2"})]


def test_create_dependency_raises_error_when_service_id_missing():
    dependency = load_dependency_module()
    with pytest.raises(ValueError, match="service_id and dependency_id are required"):
        call_fn(dependency.create_dependency, service_id=None, dependency_id="svc-2")


def test_create_dependency_raises_error_when_dependency_id_missing():
    dependency = load_dependency_module()
    with pytest.raises(ValueError, match="service_id and dependency_id are required"):
        call_fn(dependency.create_dependency, service_id="svc-1", dependency_id=None)


def test_create_dependency_raises_error_when_ids_are_same():
    dependency = load_dependency_module()
    with pytest.raises(ValueError, match="A service cannot depend on itself"):
        call_fn(dependency.create_dependency, service_id="svc-1", dependency_id="svc-1")
