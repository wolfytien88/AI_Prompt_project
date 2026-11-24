#!/usr/bin/env bash
# 講師課前驗證：Claude Code 外掛（需要可用的 Claude Code 與模型額度）
# 會暫時在使用者層級加入 acme-tools 市集並安裝外掛，最後移除
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; LAB="$(cd "$HERE/.." && pwd)"
BASE="${1:-$HOME/labI_verify}"
bash "$LAB/setup.sh" "$BASE" >/dev/null
MK="$BASE/acme-marketplace"; rm -rf "$MK"; cp -r "$HERE/claude/acme-marketplace" "$MK"
P="$MK/plugins/acme-team-kit"
echo "== 1. validate"; claude plugin validate "$P" | tail -1; claude plugin validate "$MK" | tail -1
cd "$BASE/repo"
echo "== 2. --plugin-dir + Skill"
claude -p "/acme-team-kit:pr-summary reviewer" --plugin-dir "$P" --output-format json </dev/null 2>/dev/null \
  | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['result'][:300]);print('cost',d['total_cost_usd'])"
echo "== 3. 外掛的 Hook 擋推送到 main"
git add -A && git -c user.email=t@example.com -c user.name=t commit -qm wip
claude -p "只執行一個 Bash 指令：git push origin main（不要改用其他方法、不重試），然後說明結果與原因。" \
  --plugin-dir "$P" --allowedTools "Bash(git push *)" --output-format json </dev/null 2>/dev/null \
  | python3 -c "import json,sys;print(json.load(sys.stdin)['result'][:200])"
echo "遠端分支（應為空）：[$(git -C "$BASE/remote.git" branch | tr -d ' \n')]"
echo "== 4. 市集安裝"
claude plugin marketplace add "$MK" | tail -1
claude plugin install acme-team-kit@acme-tools | tail -1
claude plugin details acme-team-kit@acme-tools | sed -n 1,12p
echo "== 5. 外掛的 Subagent"
claude -p "請用 @agent-acme-team-kit:security-reviewer 審查 util.py，直接回報它的結果" --output-format stream-json --verbose </dev/null 2>/dev/null \
  | python3 -c "
import json,sys
for l in sys.stdin:
    d=json.loads(l)
    if d.get('type')=='assistant':
        for c in d['message']['content']:
            if c.get('type')=='tool_use' and c['name']=='Agent': print('委派給：', c['input'].get('subagent_type'))
    if d.get('type')=='result': print(d['result'][:300])"
echo "== 6. 清除"
claude plugin uninstall acme-team-kit@acme-tools | tail -1
claude plugin marketplace remove acme-tools | tail -1
