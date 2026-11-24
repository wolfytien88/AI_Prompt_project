import anthropic, subprocess

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"  # 依上課當下可用的模型調整
tools = [{
    "name": "bash",
    "description": "在專案目錄執行一個 shell 指令，回傳輸出",
    "input_schema": {"type": "object",
                     "properties": {"command": {"type": "string"}},
                     "required": ["command"]},
}]
messages = [{"role": "user", "content": "執行 pytest，找出失敗原因並修好"}]

while True:
    resp = client.messages.create(model=MODEL, max_tokens=4096,
                                  tools=tools, messages=messages)
    messages.append({"role": "assistant", "content": resp.content})
    if resp.stop_reason != "tool_use":
        break  # 模型不再呼叫工具 = 完成
    results = []
    for block in resp.content:
        if block.type == "tool_use":
            out = subprocess.run(block.input["command"], shell=True,
                                 capture_output=True, text=True, timeout=60)
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": (out.stdout + out.stderr)[-5000:]})
    messages.append({"role": "user", "content": results})
print("".join(b.text for b in resp.content if b.type == "text"))
