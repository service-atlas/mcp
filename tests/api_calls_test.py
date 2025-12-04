import os
import sys
from typing import Any, Dict, Optional, Tuple

import pytest


# Ensure the 'src' directory is on sys.path so that modules like 'api_calls' can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from importlib import import_module  # noqa: E402


def load_api_calls_module(reload: bool = False):
    """Import (or reload) the api_calls module after sys.path modification."""
    if reload and "api_calls" in sys.modules:
        del sys.modules["api_calls"]
    return import_module("api_calls")


class FakeResponse:
    def __init__(self, json_data: Any, raise_error: Optional[Exception] = None):
        self._json_data = json_data
        self._raise_error = raise_error
        self.raise_called = False

    def json(self):
        return self._json_data

    def raise_for_status(self):
        self.raise_called = True
        if self._raise_error:
            raise self._raise_error


class RequestsGetSpy:
    def __init__(self, response: FakeResponse):
        self.response = response
        self.calls: list[Tuple[str, Optional[Dict[str, Any]], Optional[int]]] = []

    def __call__(self, url: str, params: Dict[str, Any] | None = None, timeout: Optional[int] = None):
        self.calls.append((url, params, timeout))
        return self.response


def test_default_base_url_used_when_env_missing(monkeypatch: pytest.MonkeyPatch):
    # Ensure API_URL is not set
    monkeypatch.delenv("API_URL", raising=False)
    api_calls = load_api_calls_module(reload=True)

    fake_resp = FakeResponse(json_data={"ok": True})
    spy = RequestsGetSpy(fake_resp)
    monkeypatch.setattr(api_calls, "requests", type("R", (), {"get": spy}))

    caller = api_calls.ApiCaller()
    data = caller.call_get("/health")

    assert data == {"ok": True}
    # Verify full URL formation and default timeout of 10
    assert spy.calls == [("http://localhost:8080/health", None, 10)]
    # Ensure raise_for_status was invoked
    assert fake_resp.raise_called is True


def test_env_base_url_used_when_set(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_URL", "https://api.example.com")
    api_calls = load_api_calls_module(reload=True)

    fake_resp = FakeResponse(json_data=[1, 2, 3])
    spy = RequestsGetSpy(fake_resp)
    monkeypatch.setattr(api_calls, "requests", type("R", (), {"get": spy}))

    caller = api_calls.ApiCaller()
    result = caller.call_get("/items")

    assert result == [1, 2, 3]
    assert spy.calls == [("https://api.example.com/items", None, 10)]


def test_call_get_normalizes_leading_slash(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_URL", "https://host")
    api_calls = load_api_calls_module(reload=True)

    fake_resp = FakeResponse(json_data={})
    spy = RequestsGetSpy(fake_resp)
    monkeypatch.setattr(api_calls, "requests", type("R", (), {"get": spy}))

    caller = api_calls.ApiCaller()
    # Call without leading slash
    caller.call_get("path")
    # Call with leading slash
    caller.call_get("/path")

    assert spy.calls == [
        ("https://host/path", None, 10),
        ("https://host/path", None, 10),
    ]


def test_call_get_passes_params_and_timeout(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_URL", "http://h")
    api_calls = load_api_calls_module(reload=True)

    fake_resp = FakeResponse(json_data={"n": 1})
    spy = RequestsGetSpy(fake_resp)
    monkeypatch.setattr(api_calls, "requests", type("R", (), {"get": spy}))

    caller = api_calls.ApiCaller()
    params = {"page": 2, "q": "abc"}
    caller.call_get("/search", params=params)

    assert spy.calls == [("http://h/search", {"page": 2, "q": "abc"}, 10)]


def test_call_get_raises_for_http_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_URL", "http://x")
    api_calls = load_api_calls_module(reload=True)

    http_error = RuntimeError("boom")
    fake_resp = FakeResponse(json_data=None, raise_error=http_error)
    spy = RequestsGetSpy(fake_resp)
    monkeypatch.setattr(api_calls, "requests", type("R", (), {"get": spy}))

    caller = api_calls.ApiCaller()

    with pytest.raises(RuntimeError) as exc:
        caller.call_get("/err")

    assert str(exc.value) == "boom"


def test_call_get_returns_json(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("API_URL", "http://y")
    api_calls = load_api_calls_module(reload=True)

    payload = {"hello": "world"}
    fake_resp = FakeResponse(json_data=payload)
    spy = RequestsGetSpy(fake_resp)
    monkeypatch.setattr(api_calls, "requests", type("R", (), {"get": spy}))

    caller = api_calls.ApiCaller()
    result = caller.call_get("/data")

    assert result == payload
    assert spy.calls == [("http://y/data", None, 10)]
