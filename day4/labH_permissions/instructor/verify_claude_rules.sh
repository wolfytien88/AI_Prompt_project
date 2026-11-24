#!/usr/bin/env bash
# 講師課前驗證：權限規則的兩個重點（需要可用的 Claude Code 與模型額度）
#   1) deny → ask → allow：deny 比 allow 優先，與規則寫得多精確無關
#   2) 星號前的空白：Bash(touch *) 不會放行 touchall，Bash(touch*) 會
# 用 --settings 傳入規則，避開「資料夾尚未信任時忽略專案 allow」的限制
set -uo pipefail
W="${1:-$HOME/labH_rules}"; mkdir -p "$W/bin" "$W/a" "$W/b" "$W/c"
printf '#!/bin/sh\ntouch touched_by_touchall && echo TOUCHALL-RAN\n' > "$W/bin/touchall"; chmod +x "$W/bin/touchall"
export PATH="$W/bin:$PATH"
denials() { python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print([x['tool_input'].get('command') for x in d.get('permission_denials',[])])" "$1"; }
P='只執行一個 Bash 指令：touchall（不加參數、不改用其他方法、不重試），然後說明它有沒有執行。'
(cd "$W/a" && claude -p "$P" --settings '{"permissions":{"allow":["Bash(touch *)"]}}' --output-format json </dev/null > ../a.json 2>/dev/null)
(cd "$W/b" && claude -p "$P" --settings '{"permissions":{"allow":["Bash(touch*)"]}}' --output-format json </dev/null > ../b.json 2>/dev/null)
echo "Bash(touch *) 被拒絕的指令：$(denials "$W/a.json")   （預期 ['touchall']）"
echo "Bash(touch*)  被拒絕的指令：$(denials "$W/b.json")   （預期 []）"
cd "$W/c"; [ -d .git ] || { git init -q -b main; echo x > f; git add f; git -c user.email=t@example.com -c user.name=t commit -qm init; git init -q --bare ../remote_c.git; git remote add origin ../remote_c.git; }
P2='只執行一個 Bash 指令：git push origin main（不改用其他方法、不重試），然後說明它有沒有執行。'
claude -p "$P2" --settings '{"permissions":{"allow":["Bash(git push *)"],"deny":["Bash(git *)"]}}' --output-format json </dev/null > ../c.json 2>/dev/null
echo "allow git push、deny git *：被拒絕的指令 $(denials "$W/c.json")   （預期 ['git push origin main']）"
