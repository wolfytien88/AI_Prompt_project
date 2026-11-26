import json, subprocess
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-5"  # 依上課當下可用的模型調整
tools = [{
    "type": "function",
    "name": "bash",
    "description": "在專案目錄執行一個 shell 指令，回傳輸出",
    "parameters": {"type": "object",
                   "properties": {"command": {"type": "string"}},
                   "required": ["command"]},
}]
inputs = [{"role": "user", "content": "執行 pytest，找出失敗原因並修好"}]

rounds, input_tokens, output_tokens = 0, 0, 0
while True:
    resp = client.responses.create(model=MODEL, tools=tools, input=inputs)
    rounds += 1
    input_tokens += resp.usage.input_tokens
    output_tokens += resp.usage.output_tokens
    inputs += resp.output  # 把模型這一輪的輸出（含 function_call）接回對話
    calls = [o for o in resp.output if o.type == "function_call"]
    if not calls:
        break  # 模型不再呼叫工具 = 完成
    for call in calls:
        cmd = json.loads(call.arguments)["command"]
        print(f"[第 {rounds} 輪] $ {cmd}")
        out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60,
                             encoding="utf-8", errors="replace")
        inputs.append({"type": "function_call_output", "call_id": call.call_id,
                       "output": (out.stdout + out.stderr)[-5000:]})
print(resp.output_text)
print(f"輪數：{rounds}　輸入 Token：{input_tokens}　輸出 Token：{output_tokens}")
