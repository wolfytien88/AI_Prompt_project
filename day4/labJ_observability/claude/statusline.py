#!/usr/bin/env python3
"""statusline.sh 的 Python 版（不需要 jq，Windows 也能用）。
settings.json："statusLine": {"type": "command", "command": "python3 /絕對路徑/statusline.py"}
"""
import json, os, sys


def get(d, *keys):
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


d = json.load(sys.stdin)
model = get(d, "model", "display_name") or "?"
pct = int(float(get(d, "context_window", "used_percentage") or 0))
cost = float(get(d, "cost", "total_cost_usd") or 0)
cwd = os.path.basename(get(d, "workspace", "current_dir") or "")
rl = get(d, "rate_limits", "five_hour", "used_percentage")
color = "\033[31m" if pct >= 85 else "\033[33m" if pct >= 70 else "\033[32m"
line = f"[{model}] {color}ctx {pct}%\033[0m | ${cost:.2f} | {cwd}"
if rl is not None:
    line += f" | 5h {int(float(rl))}%"
print(line)
