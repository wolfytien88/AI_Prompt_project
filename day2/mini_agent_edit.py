"""實作 4 參考版：mini_agent.py 加上宣告式 read_file 與 edit_file 工具（含過期檢查）。

用法：在要修的專案資料夾內執行
    python3 ../mini_agent_edit.py      （Windows：python ..\\mini_agent_edit.py）
"""
import os, sys, subprocess

import anthropic

from edit_tool import read_file, edit_file

# Windows：shell=True 走 cmd.exe，python3 通常是 Microsoft Store 空殼；子程序輸出一律用 UTF-8 解讀
IS_WINDOWS = os.name == "nt"
PY = "python" if IS_WINDOWS else "python3"
SHELL_NOTE = "（Windows cmd.exe：請用 dir、type 等指令，Python 請用 python 而非 python3）" if IS_WINDOWS else ""
CHILD_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")   # 主控台是 cp950 時，印不出的字元改成 ? 而不是中斷

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"  # 依上課當下可用的模型調整
tools = [
    {
        "name": "bash",
        "description": "在專案目錄執行一個 shell 指令（執行測試、列出檔案），回傳輸出。修改檔案請用 edit_file。" + SHELL_NOTE,
        "input_schema": {"type": "object",
                         "properties": {"command": {"type": "string"}},
                         "required": ["command"]},
    },
    {
        "name": "read_file",
        "description": "讀取一個文字檔的完整內容。修改檔案前必須先讀取。",
        "input_schema": {"type": "object",
                         "properties": {"path": {"type": "string"}},
                         "required": ["path"]},
    },
    {
        "name": "edit_file",
        "description": "把檔案中剛好出現一次的 old 字串換成 new。檔案在上次讀取後被改過會被拒絕，需重新讀取。",
        "input_schema": {"type": "object",
                         "properties": {"path": {"type": "string"},
                                        "old": {"type": "string"},
                                        "new": {"type": "string"}},
                         "required": ["path", "old", "new"]},
    },
]


def run_tool(name, args):
    """Harness 依工具名稱分派；參數有型別，可以在這裡加上檢查或記錄。"""
    try:
        if name == "bash":
            out = subprocess.run(args["command"], shell=True,
                                 capture_output=True, text=True, timeout=60,
                                 encoding="utf-8", errors="replace", env=CHILD_ENV)
            return (out.stdout + out.stderr)[-5000:]
        if name == "read_file":
            return read_file(args["path"])[-20000:]
        if name == "edit_file":
            print(f"  edit {args['path']}: {args['old']!r} → {args['new']!r}")
            return edit_file(args["path"], args["old"], args["new"])
        return f"錯誤：沒有名為 {name} 的工具"
    except Exception as e:  # 例如檔案不存在：把錯誤回給模型，而不是讓 Agent 中斷
        return f"錯誤：{type(e).__name__}: {e}"


def main():
    messages = [{"role": "user", "content": f"執行 {PY} -m pytest -q，找出失敗原因並修好。只能修改 shop/ 底下的程式，不要改測試。"}]
    while True:
        resp = client.messages.create(model=MODEL, max_tokens=4096,
                                      tools=tools, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})
        if resp.stop_reason != "tool_use":
            break
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                print(f"$ {block.name} {block.input}")
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": run_tool(block.name, block.input)})
        messages.append({"role": "user", "content": results})
    print("".join(b.text for b in resp.content if b.type == "text"))


if __name__ == "__main__":
    main()
