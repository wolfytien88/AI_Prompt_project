#!/usr/bin/env python3
"""講師課前驗證用的假 OpenAI Responses API（串流），給 Codex SDK 範例使用。

不連 OpenAI、不需要 API Key。依序要求 Codex 執行 MOCK_CMDS 裡的 shell 指令，
指令都送完後回一則助理訊息：MOCK_TEXT（若請求帶有 JSON Schema，改回 MOCK_JSON）。
模型的回覆是假的，但 Codex 執行指令、沙箱、事件串流與 Session 接續都是真的。

用法：MOCK_CMDS='["ls"]' MOCK_JSON='{"tests_passed":true,"bugs":[]}' python3 mock_codex_agent.py 8767
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

CMDS = json.loads(os.environ.get("MOCK_CMDS", '["echo hello"]'))
TEXT = os.environ.get("MOCK_TEXT", "模擬回覆：已完成")
JSON_TEXT = os.environ.get("MOCK_JSON", "{}")
LOG_PATH = os.environ.get("MOCK_LOG", "mock_requests.jsonl")
TOOL = os.environ.get("MOCK_TOOL", "exec_command")


def sse(w, ev):
    w.write(f"event: {ev['type']}\ndata: {json.dumps(ev)}\n\n".encode())


class Handler(BaseHTTPRequestHandler):
    count = 0

    def log_message(self, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"data":[],"models":[]}')

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["content-length"])))
        items = body.get("input", [])
        outputs = [i for i in items if isinstance(i, dict) and i.get("type") == "function_call_output"]
        fmt = (body.get("text") or {}).get("format") or {}
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps({"n_input_items": len(items), "n_tool_outputs": len(outputs),
                                "schema": fmt.get("type")}, ensure_ascii=False) + "\n")
        Handler.count += 1
        n = Handler.count
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.end_headers()
        sse(self.wfile, {"type": "response.created", "response": {"id": f"resp_{n}"}})
        if len(outputs) < len(CMDS):
            args = {"cmd": CMDS[len(outputs)]} if TOOL == "exec_command" else {"command": ["bash", "-lc", CMDS[len(outputs)]]}
            item = {"type": "function_call", "id": f"fc_{n}", "call_id": f"call_{n}",
                    "name": TOOL, "arguments": json.dumps(args)}
        else:
            text = JSON_TEXT if fmt.get("type") == "json_schema" else TEXT
            item = {"type": "message", "role": "assistant", "id": f"msg_{n}",
                    "content": [{"type": "output_text", "text": text, "annotations": []}]}
        sse(self.wfile, {"type": "response.output_item.done", "item": item})
        sse(self.wfile, {"type": "response.completed", "response": {"id": f"resp_{n}", "usage": {
            "input_tokens": 1, "output_tokens": 1, "total_tokens": 2,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens_details": {"reasoning_tokens": 0}}}})


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", int(sys.argv[1])), Handler).serve_forever()
