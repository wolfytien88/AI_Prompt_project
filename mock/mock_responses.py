# 假的 OpenAI Responses API：第一輪要求執行 SCRIPT 中的指令，收到工具結果後回最終訊息
import json, sys, os
from http.server import BaseHTTPRequestHandler, HTTPServer
LOG = open("mock_requests.jsonl", "a")
CMDS = json.loads(os.environ.get("MOCK_CMDS", '["echo hello"]'))
TOOL = os.environ.get("MOCK_TOOL", "")  # 由第一次探測得知
n = 0
def sse(w, ev): w.write(f"event: {ev['type']}\ndata: {json.dumps(ev)}\n\n".encode())
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        self.send_response(200); self.send_header("content-type","application/json"); self.end_headers()
        self.wfile.write(b'{"data":[],"models":[]}')
    def do_POST(self):
        global n
        body = json.loads(self.rfile.read(int(self.headers["content-length"])))
        open("full_req.json","w").write(json.dumps(body,ensure_ascii=False)) # FULL
        LOG.write(json.dumps({"path": self.path, "tools": [t.get("name") or t.get("type") for t in body.get("tools", [])],
                              "input_tail": body.get("input", [])[-1:]}, ensure_ascii=False) + "\n"); LOG.flush()
        outs = [i for i in body.get("input", []) if i.get("type") == "function_call_output"]
        self.send_response(200); self.send_header("content-type", "text/event-stream"); self.end_headers()
        rid = f"resp_{n}"; n += 1
        sse(self.wfile, {"type": "response.created", "response": {"id": rid}})
        if TOOL and len(outs) < len(CMDS):
            cmd = CMDS[len(outs)]
            args = {"command": ["bash", "-lc", cmd]} if TOOL == "shell" else {"cmd": cmd} if TOOL == "exec_command" else {"command": cmd}
            item = {"type": "function_call", "id": f"fc_{n}", "call_id": f"call_{n}", "name": TOOL, "arguments": json.dumps(args)}
        else:
            item = {"type": "message", "role": "assistant", "id": f"msg_{n}",
                    "content": [{"type": "output_text", "text": "測試結束", "annotations": []}]}
        sse(self.wfile, {"type": "response.output_item.done", "item": item})
        sse(self.wfile, {"type": "response.completed", "response": {"id": rid, "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2, "input_tokens_details": {"cached_tokens": 0}, "output_tokens_details": {"reasoning_tokens": 0}}}})
HTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
