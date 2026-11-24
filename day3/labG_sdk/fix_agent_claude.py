"""用 Claude Agent SDK 寫的修 bug Agent。

用法：
  python3 fix_agent_claude.py <專案資料夾>                 # 修 bug，印出事件與成本
  python3 fix_agent_claude.py <專案資料夾> --resume <ID>   # 接續同一個 Session，要求結構化摘要

需要：pip install claude-agent-sdk、環境變數 ANTHROPIC_API_KEY（SDK 不會自動讀 .env）
"""
import argparse
import asyncio
import json

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
    UserMessage,
    query,
)

TASK = """執行 `python3 -m unittest discover -s tests`，找出失敗原因並修正 invoice/calc.py。
規則：只能修改 invoice/calc.py，不要改測試；改完再執行一次測試確認全部通過；最後用兩三句話說明每個 bug 的原因。"""

SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "tests_passed": {"type": "boolean"},
        "bugs": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "function": {"type": "string"},
                    "cause": {"type": "string"},
                    "fix": {"type": "string"},
                },
                "required": ["function", "cause", "fix"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["tests_passed", "bugs"],
    "additionalProperties": False,
}


def show(msg):
    """把 SDK 送來的每則訊息印成一行，方便觀察 Agent Loop。"""
    if isinstance(msg, SystemMessage):
        print(f"[system] {msg.subtype}")
    elif isinstance(msg, AssistantMessage):
        for b in msg.content:
            if isinstance(b, ToolUseBlock):
                arg = b.input.get("command") or b.input.get("file_path") or ""
                print(f"[tool]   {b.name} {arg}")
            elif isinstance(b, TextBlock) and b.text.strip():
                print(f"[text]   {b.text.strip()[:200]}")
    elif isinstance(msg, UserMessage):
        print("[result] 工具結果已送回模型")
    elif isinstance(msg, ResultMessage):
        print(f"[done]   subtype={msg.subtype} turns={msg.num_turns} "
              f"cost=${(msg.total_cost_usd or 0):.4f} session={msg.session_id}")
        if msg.permission_denials:
            print(f"[deny]   {msg.permission_denials}")


async def fix(project):
    options = ClaudeAgentOptions(
        cwd=project,
        allowed_tools=["Read", "Glob", "Grep", "Edit", "Bash(python3 -m unittest *)"],
        disallowed_tools=["Write", "WebFetch", "WebSearch"],
        permission_mode="acceptEdits",   # 編輯自動核准；其他需要詢問的動作在 SDK 中會被拒絕
        max_turns=20,
        max_budget_usd=1.0,
    )
    async for msg in query(prompt=TASK, options=options):
        show(msg)


async def summarize(project, session_id):
    options = ClaudeAgentOptions(
        cwd=project,
        resume=session_id,                # 接續剛才的 Session，不必重新讀檔
        allowed_tools=["Read"],
        max_turns=5,
        output_format={"type": "json_schema", "schema": SUMMARY_SCHEMA},
    )
    async for msg in query(prompt="依照剛才的修正，輸出摘要。", options=options):
        if isinstance(msg, ResultMessage):
            print(json.dumps(msg.structured_output, ensure_ascii=False, indent=2))
            print(f"[done]   cost=${(msg.total_cost_usd or 0):.4f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--resume", help="上一次輸出的 session ID")
    a = ap.parse_args()
    asyncio.run(summarize(a.project, a.resume) if a.resume else fix(a.project))
