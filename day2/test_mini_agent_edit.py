"""mini_agent_edit.py 的工具分派測試（不呼叫模型）：python3 -m pytest -q test_mini_agent_edit.py"""
import os

os.environ.setdefault("ANTHROPIC_API_KEY", "x")   # 建立 client 需要，測試不會呼叫 API

import edit_tool
from mini_agent_edit import run_tool


def test_bash_tool(tmp_path):
    assert run_tool("bash", {"command": "echo hello"}).strip() == "hello"


def test_read_then_edit(tmp_path):
    edit_tool.read_times.clear()
    p = tmp_path / "f.py"
    p.write_text("a = 1\n", encoding="utf-8")
    assert run_tool("read_file", {"path": str(p)}) == "a = 1\n"
    assert run_tool("edit_file", {"path": str(p), "old": "a = 1", "new": "a = 2"}) == "已修改"
    assert p.read_text(encoding="utf-8") == "a = 2\n"


def test_edit_without_read_rejected(tmp_path):
    edit_tool.read_times.clear()
    p = tmp_path / "g.py"
    p.write_text("b = 1\n", encoding="utf-8")
    assert run_tool("edit_file", {"path": str(p), "old": "b = 1", "new": "b = 2"}).startswith("錯誤")


def test_missing_file_returns_error_text(tmp_path):
    assert run_tool("read_file", {"path": str(tmp_path / "nope.py")}).startswith("錯誤：FileNotFoundError")


def test_unknown_tool():
    assert run_tool("delete_all", {}) == "錯誤：沒有名為 delete_all 的工具"
