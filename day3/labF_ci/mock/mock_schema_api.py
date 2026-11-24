#!/usr/bin/env python3
"""講師課前驗證用的假 OpenAI Responses API（串流）。

不連 OpenAI、不需要 API Key。每次請求都回一則固定的助理訊息（MOCK_TEXT），
並把 Codex 送出的 text.format（--output-schema 轉成的 JSON Schema）記到 MOCK_LOG。
回覆內容是假的，用途是確認 codex exec 的參數、Schema 傳遞與 -o 輸出檔流程。

用法：MOCK_TEXT='{"status":"pass",...}' MOCK_LOG=req.jsonl python3 mock_schema_api.py 8766
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

TEXT = os.environ.get("MOCK_TEXT", "{}")
LOG = os.environ.get("MOCK_LOG", "mock_requests.jsonl")


def sse(w, ev):
    w.write(f"event: {ev['type']}\ndata: {json.dumps(ev)}\n\n".encode())


class Handler(BaseHTTPRequestHandler):
    n = 0

    def log_message(self, *a):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"data":[],"models":[]}')

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["content-length"])))
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"path": self.path, "model": body.get("model"),
                                "text": body.get("text"),
                                "tools": [t.get("name") or t.get("type") for t in body.get("tools", [])]},
                               ensure_ascii=False) + "\n")
        Handler.n += 1
        rid = f"resp_{Handler.n}"
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.end_headers()
        sse(self.wfile, {"type": "response.created", "response": {"id": rid}})
        item = {"type": "message", "role": "assistant", "id": f"msg_{Handler.n}",
                "content": [{"type": "output_text", "text": TEXT, "annotations": []}]}
        sse(self.wfile, {"type": "response.output_item.done", "item": item})
        sse(self.wfile, {"type": "response.completed", "response": {"id": rid, "usage": {
            "input_tokens": 1, "output_tokens": 1, "total_tokens": 2,
            "input_tokens_details": {"cached_tokens": 0}, "output_tokens_details": {"reasoning_tokens": 0}}}})


HTTPServer(("127.0.0.1", int(sys.argv[1])), Handler).serve_forever()
