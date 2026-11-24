#!/usr/bin/env python3
"""Codex 的 notify 腳本：每一輪結束時，Codex 會把一個 JSON 字串當成第一個參數傳進來。

在 ~/.codex/config.toml 設定（只能放在使用者層級，專案的 .codex/config.toml 不能設 notify）：
    notify = ["python3", "/絕對路徑/notify.py"]

這支腳本做兩件事：
  1. 把事件附加到 ~/.codex/turns.jsonl（可用環境變數 CODEX_NOTIFY_LOG 改位置），之後給 cost_log.py 彙整
  2. 在終端機印一行摘要；macOS 上若有 osascript 會跳出系統通知
"""
import json, os, shutil, subprocess, sys, datetime

def main() -> int:
    if len(sys.argv) < 2:
        print("用法：notify.py '<JSON>'", file=sys.stderr)
        return 1
    try:
        ev = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print("notify.py：收到的不是 JSON", file=sys.stderr)
        return 1
    if ev.get("type") != "agent-turn-complete":      # 目前只有這一種事件
        return 0
    log = os.environ.get("CODEX_NOTIFY_LOG", os.path.expanduser("~/.codex/turns.jsonl"))
    os.makedirs(os.path.dirname(log), exist_ok=True)
    rec = {
        "time": datetime.datetime.now().isoformat(timespec="seconds"),
        "thread_id": ev.get("thread-id"),
        "turn_id": ev.get("turn-id"),
        "cwd": ev.get("cwd"),
        "input": " / ".join(ev.get("input-messages") or [])[:200],
        "last_message": (ev.get("last-assistant-message") or "")[:200],
    }
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    summary = f"Codex 完成一輪｜{os.path.basename(rec['cwd'] or '')}｜{rec['last_message'][:60]}"
    print(summary)
    if shutil.which("osascript"):
        subprocess.run(["osascript", "-e", f'display notification "{rec["last_message"][:80]}" with title "Codex"'],
                       check=False)
    return 0

if __name__ == "__main__":
    sys.exit(main())
