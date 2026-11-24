"""實作 4 參考版：mini_agent.py 加上宣告式 read_file 與 edit_file 工具（含過期檢查）。

用法：在要修的專案資料夾內執行
    python3 ../mini_agent_edit.py
"""
import anthropic, subprocess

from edit_tool import read_file, edit_file

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"  # 依上課當下可用的模型調整
tools = [
    {
        "name": "bash",
        "description": "在專案目錄執行一個 shell 指令（執行測試、列出檔案），回傳輸出。修改檔案請用 edit_file。",
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
                                 capture_output=True, text=True, timeout=60)
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
    messages = [{"role": "user", "content": "執行 python3 -m pytest -q，找出失敗原因並修好。只能修改 shop/ 底下的程式，不要改測試。"}]
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
