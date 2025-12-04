import os
import sys
from typing import Any, List, Tuple

import pytest


# Ensure the 'src' directory is on sys.path so that modules like 'debt' can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from importlib import import_module  # noqa: E402


def load_debt_module():
    # Import lazily after sys.path modification so static analyzers don't fail
    return import_module("debt")


class DummyApiCaller:
    def __init__(self, response: Any):
        self.response = response
        self.calls: List[Tuple[str, Any]] = []

    def call_get(self, url: str, params: dict | None = None):
        self.calls.append((url, params))
        return self.response


def test_prompt_get_debt_mentions_tools_and_resources():
    debt = load_debt_module()
    prompt = debt.prompt_get_debt.fn()
    assert "get_debt" in prompt
    assert "serviceatlas://debts" in prompt
    assert "get_debts_for_service" in prompt
    assert "serviceatlas://debts/{service_id}" in prompt


def test_get_debt_tool_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    debt = load_debt_module()
    fake_response = [
        {"name": "orders", "count": 5, "id": "svc-1"},
        {"name": "billing", "count": 2, "id": "svc-2"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(debt, "api_caller", dummy, raising=True)

    result = debt.get_debt.fn()

    assert result == fake_response
    assert dummy.calls == [("/reports/services/debt", None)]


def test_get_debts_resource_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    debt = load_debt_module()
    fake_response = [
        {"name": "orders", "count": 5, "id": "svc-1"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(debt, "api_caller", dummy, raising=True)

    result = debt.get_debts_resource.fn()

    assert result == fake_response
    assert dummy.calls == [("/reports/services/debt", None)]


def test_get_debts_for_service_tool_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    debt = load_debt_module()
    fake_response = [
        {"id": "deb-1", "type": "security", "title": "Update library"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(debt, "api_caller", dummy, raising=True)

    result = debt.get_debts_for_service.fn("svc-123")

    assert result == fake_response
    assert dummy.calls == [("/services/svc-123/debt", None)]


def test_get_debts_for_service_resource_calls_api_and_returns_data(monkeypatch: pytest.MonkeyPatch):
    debt = load_debt_module()
    fake_response = [
        {"id": "deb-9", "type": "ops", "title": "Rotate keys"},
    ]
    dummy = DummyApiCaller(fake_response)
    monkeypatch.setattr(debt, "api_caller", dummy, raising=True)

    result = debt.get_debts_for_service_resource.fn("svc-xyz")

    assert result == fake_response
    assert dummy.calls == [("/services/svc-xyz/debt", None)]
