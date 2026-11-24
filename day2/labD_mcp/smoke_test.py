"""不經過任何 Agent，直接用 JSON-RPC 測試 MCP Server。
用法：ORDERS_DB=./orders.db python3 smoke_test.py [server 檔案，預設 orders_server.py]
"""
import json
import os
import subprocess
import sys

server = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "orders_server.py")
p = subprocess.Popen([sys.executable, server], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=os.environ)
n = 0


def send(method, params=None, notify=False):
    global n
    msg = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        msg["params"] = params
    if not notify:
        n += 1
        msg["id"] = n
    p.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n"); p.stdin.flush()
    if notify:
        return None
    while True:
        line = p.stdout.readline()
        if not line:
            raise SystemExit("Server 沒有回應")
        r = json.loads(line)
        if r.get("id") == n:
            return r


init = send("initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "smoke", "version": "1"}})
print("server:", init["result"]["serverInfo"])
send("notifications/initialized", notify=True)
tools = send("tools/list")["result"]["tools"]
for t in tools:
    ann = t.get("annotations") or {}
    print(f"  tool {t['name']:<22} readOnly={ann.get('readOnlyHint')}")
r = send("tools/call", {"name": "order_summary", "arguments": {"month": "2026-10"}})
print("order_summary(2026-10):", r["result"]["content"][0]["text"][:300])
r = send("tools/call", {"name": "update_order_status", "arguments": {"order_id": "O-9999", "status": "shipped"}})
print("update_order_status(O-9999):", "isError" if r.get("result", {}).get("isError") or "error" in r else "ok", json.dumps(r, ensure_ascii=False)[:200])
p.stdin.close(); p.terminate()
