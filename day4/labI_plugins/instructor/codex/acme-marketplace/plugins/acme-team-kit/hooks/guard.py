#!/usr/bin/env python3
import json, re, sys

cmd = json.load(sys.stdin).get("tool_input", {}).get("command", "")
rules = [
    (r"rm\s+-rf\s+(/|~)(\*|\s|$)", "禁止刪除根目錄或家目錄"),
    (r"git\s+push\b.*(?<![\w/.-])(main|master)(?![\w/.-])", "禁止直接推送到 main，請開 PR"),
]
for pattern, reason in rules:
    if re.search(pattern, cmd):
        print(reason, file=sys.stderr)  # 理由會回饋給模型
        sys.exit(2)                     # exit code 2 = 阻擋這次工具呼叫
sys.exit(0)
