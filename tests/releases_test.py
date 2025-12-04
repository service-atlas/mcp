import os
import sys
from typing import Any, List, Tuple

import pytest


# Ensure the 'src' directory is on sys.path so that modules like 'releases' can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from importlib import import_module  # noqa: E402


def load_releases_module():
    # Import lazily after sys.path modification so static analyzers don't fail
    return import_module("releases")


class DummyApiCaller:
    def __init__(self, response: Any):
        self.response = response
        self.calls: List[Tuple[str, Any]] = []

    def call_get(self, url: str, params: dict | None = None):
        self.calls.append((url, params))
        return self.response


def test_prompt_get_releases():
    releases = load_releases_module()
    prompt = releases.prompt_get_releases.fn("2024-01-01", "2024-01-31")
    # Check that the prompt references both the tool and the resource URI with provided dates
    assert "get_releases" in prompt
    assert "serviceatlas://releases/2024-01-01/2024-01-31" in prompt
    assert "array of release objects" in prompt


def test_get_releases_tool_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    releases = load_releases_module()
    fake_response = [
        {"service": "orders", "service_id": "svc-1", "version": "1.2.3", "release_date": "2024-01-02"}
    ]
    dummy = DummyApiCaller(fake_response)
    # Patch the module-level api_caller used inside releases.get_releases
    monkeypatch.setattr(releases, "api_caller", dummy, raising=True)

    result = releases.get_releases.fn("2024-01-01", "2024-01-31")

    assert result == fake_response
    # Verify proper URL formation with leading slash
    assert dummy.calls == [("/releases/2024-01-01/2024-01-31", None)]


def test_get_releases_resource_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    releases = load_releases_module()
    fake_response = [
        {"service": "billing", "service_id": "svc-2", "version": "2.0.0", "release_date": "2024-02-10"}
    ]
    dummy = DummyApiCaller(fake_response)
    # Patch the module-level api_caller used inside releases.get_releases_resource
    monkeypatch.setattr(releases, "api_caller", dummy, raising=True)

    result = releases.get_releases_resource.fn("2024-02-01", "2024-02-29")

    assert result == fake_response
    assert dummy.calls == [("/releases/2024-02-01/2024-02-29", None)]
