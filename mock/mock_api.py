# 模擬 Anthropic Messages API 與 OpenAI Responses API（非串流），記錄每次請求
import json, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
LOG = open("api_requests.jsonl", "w")
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def reply(self, obj):
        b = json.dumps(obj).encode(); self.send_response(200)
        self.send_header("content-type", "application/json"); self.send_header("content-length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["content-length"])))
        LOG.write(json.dumps({"path": self.path, "body": body}, ensure_ascii=False) + "\n"); LOG.flush()
        if self.path.endswith("/messages"):
            msgs = body["messages"]; last = msgs[-1]["content"]
            has_result = isinstance(last, list) and any(b.get("type") == "tool_result" for b in last)
            if body.get("tools") and not has_result:
                content, stop = [{"type": "tool_use", "id": "toolu_1", "name": "bash", "input": {"command": "python3 -c 'print(6*7)'"}}], "tool_use"
            else:
                text = f"[mock] system={body.get('system','')[:10]} | 回覆：{last if isinstance(last,str) else '收到工具結果 ' + last[0]['content'][:20]}"
                content, stop = [{"type": "text", "text": text}], "end_turn"
            self.reply({"id": "msg_1", "type": "message", "role": "assistant", "model": body["model"], "content": content,
                        "stop_reason": stop, "stop_sequence": None, "usage": {"input_tokens": 1, "output_tokens": 1}})
        elif self.path.endswith("/responses"):
            inp = body["input"]; inp = inp if isinstance(inp, list) else [{"role": "user", "content": inp}]
            has_out = any(isinstance(i, dict) and i.get("type") == "function_call_output" for i in inp)
            if body.get("tools") and not has_out:
                out = [{"type": "function_call", "id": "fc_1", "call_id": "call_1", "name": "bash", "arguments": json.dumps({"command": "python3 -c 'print(6*7)'"}), "status": "completed"}]
            else:
                fco = [i for i in inp if isinstance(i, dict) and i.get("type") == "function_call_output"]
                text = f"[mock] instructions={str(body.get('instructions'))[:10]} | 回覆：{fco[-1]['output'][:20] if fco else inp[-1]['content']}"
                out = [{"type": "message", "id": "msg_1", "role": "assistant", "status": "completed", "content": [{"type": "output_text", "text": text, "annotations": []}]}]
            self.reply({"id": "resp_1", "object": "response", "created_at": 0, "model": body["model"], "status": "completed", "output": out,
                        "parallel_tool_calls": True, "tool_choice": "auto", "tools": [], "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}})
HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
