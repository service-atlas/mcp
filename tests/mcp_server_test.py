import os
import sys

import pytest


# Ensure the 'src' directory is on sys.path so that modules like 'mcp_server' can be imported.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SRC_PATH = os.path.join(PROJECT_ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from importlib import import_module  # noqa: E402


class DummyMCP:
    def __init__(self):
        self.import_calls = []
        self.run_called = 0

    async def import_server(self, server):
        self.import_calls.append(server)

    def run(self):
        self.run_called += 1


def load_mcp_server_module():
    # Import lazily after sys.path modification so static analyzers don't fail
    return import_module("mcp_server")


@pytest.mark.asyncio
async def test_setup_imports_servers_in_order(monkeypatch: pytest.MonkeyPatch):
    mcp_server = load_mcp_server_module()
    dummy = DummyMCP()
    # Replace the global mcp with our dummy to capture imports
    monkeypatch.setattr(mcp_server, "mcp", dummy, raising=True)

    await mcp_server.setup()

    assert dummy.import_calls == [
        mcp_server.debt_mcp,
        mcp_server.teams_mcp,
        mcp_server.service_mcp,
        mcp_server.release_mcp,
    ]


def test_main_runs_setup_then_mcp_run(monkeypatch: pytest.MonkeyPatch):
    mcp_server = load_mcp_server_module()
    dummy = DummyMCP()
    flag = {"called": False}

    async def fake_setup():
        flag["called"] = True

    monkeypatch.setattr(mcp_server, "mcp", dummy, raising=True)
    monkeypatch.setattr(mcp_server, "setup", fake_setup, raising=True)

    mcp_server.main()

    assert flag["called"] is True
    assert dummy.run_called == 1


def test_main_handles_keyboard_interrupt(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    mcp_server = load_mcp_server_module()

    async def raise_kbi():
        raise KeyboardInterrupt

    monkeypatch.setattr(mcp_server, "setup", raise_kbi, raising=True)

    # Should not raise SystemExit(1)
    mcp_server.main()

    err = capsys.readouterr().err
    assert "Server shutdown requested by user" in err


def test_main_logs_error_and_exits_with_code_1(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    mcp_server = load_mcp_server_module()

    async def raise_error():
        raise RuntimeError("boom")

    def fake_exit(code):
        raise SystemExit(code)

    monkeypatch.setattr(mcp_server, "setup", raise_error, raising=True)
    monkeypatch.setattr(mcp_server.sys, "exit", fake_exit, raising=True)

    with pytest.raises(SystemExit) as exc:
        mcp_server.main()

    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "Failed to start MCP Server: boom" in err
