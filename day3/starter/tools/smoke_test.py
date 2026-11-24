"""基本端對端檢查：Session 開場第 5 步用。伺服器需已由 ./init.sh 啟動。

用法：python3 tools/smoke_test.py [網址，預設 http://localhost:5173]
"""
import json
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5173"


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=5) as r:
        return r.status, r.read().decode("utf-8")


def main() -> int:
    failures = []
    try:
        status, body = get("/api/health")
        if status != 200 or json.loads(body).get("status") != "ok":
            failures.append("/api/health 沒有回傳 {\"status\": \"ok\"}")
        status, body = get("/api/todos")
        if status != 200 or not isinstance(json.loads(body), list):
            failures.append("/api/todos 沒有回傳 JSON 陣列")
        status, body = get("/")
        if status != 200 or "<title>待辦清單</title>" not in body:
            failures.append("首頁沒有正確回傳")
    except OSError as e:
        failures.append(f"無法連線到 {BASE}：{e}。請先執行 ./init.sh")
    if failures:
        for f in failures:
            print("FAIL", f)
        return 1
    print("PASS 基本端對端檢查通過")
    return 0


if __name__ == "__main__":
    sys.exit(main())
