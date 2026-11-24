#!/usr/bin/env python3
"""給講師課前驗證用的假 OpenAI Responses API（串流）。

不連 OpenAI、不需要 API Key。Codex 每送一次請求，這個伺服器就依序要求它執行
MOCK_CMDS 裡的一個 shell 指令；指令都送完後回一則「測試結束」訊息。
模型的回覆是假的，但 Codex 的 Hook、權限與沙箱都是真的在執行。

用法：MOCK_CMDS='["git push origin main"]' MOCK_LOG=requests.jsonl python3 mock_codex.py 8765
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

CMDS = json.loads(os.environ.get("MOCK_CMDS", '["echo hello"]'))
LOG_PATH = os.environ.get("MOCK_LOG", "mock_requests.jsonl")
TOOL = os.environ.get("MOCK_TOOL", "exec_command")  # Codex 0.164.0 的 shell 工具名稱


def sse(w, ev):
    w.write(f"event: {ev['type']}\ndata: {json.dumps(ev)}\n\n".encode())


class Handler(BaseHTTPRequestHandler):
    count = 0

    def log_message(self, *args):
        pass

    def do_GET(self):  # Codex 可能查詢模型清單
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"data":[],"models":[]}')

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["content-length"])))
        items = body.get("input", [])
        outputs = [i for i in items if isinstance(i, dict) and i.get("type") == "function_call_output"]
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "tools": [t.get("name") or t.get("type") for t in body.get("tools", [])],
                "function_call_outputs": [str(o.get("output")) for o in outputs],
            }, ensure_ascii=False) + "\n")
        Handler.count += 1
        n = Handler.count
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.end_headers()
        sse(self.wfile, {"type": "response.created", "response": {"id": f"resp_{n}"}})
        if len(outputs) < len(CMDS):
            cmd = CMDS[len(outputs)]
            args = {"cmd": cmd} if TOOL == "exec_command" else {"command": ["bash", "-lc", cmd]}
            item = {"type": "function_call", "id": f"fc_{n}", "call_id": f"call_{n}",
                    "name": TOOL, "arguments": json.dumps(args)}
        else:
            item = {"type": "message", "role": "assistant", "id": f"msg_{n}",
                    "content": [{"type": "output_text", "text": "測試結束", "annotations": []}]}
        sse(self.wfile, {"type": "response.output_item.done", "item": item})
        sse(self.wfile, {"type": "response.completed", "response": {"id": f"resp_{n}", "usage": {
            "input_tokens": 1, "output_tokens": 1, "total_tokens": 2,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens_details": {"reasoning_tokens": 0}}}})


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", int(sys.argv[1])), Handler).serve_forever()
