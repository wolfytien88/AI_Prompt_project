#!/usr/bin/env bash
# Claude Code 狀態列：模型｜上下文用量｜本次費用｜目錄（需要 jq；沒有 jq 時改用 statusline.py）
# Claude Code 會把狀態 JSON 從 stdin 傳進來，這支腳本印出的第一行就是狀態列
input=$(cat)
MODEL=$(echo "$input" | jq -r '.model.display_name // "?"')
PCT=$(echo "$input"   | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
COST=$(echo "$input"  | jq -r '.cost.total_cost_usd // 0')
DIR=$(echo "$input"   | jq -r '.workspace.current_dir // ""')
RL=$(echo "$input"    | jq -r '.rate_limits.five_hour.used_percentage // empty' | cut -d. -f1)

# 上下文超過 70% 變黃、超過 85% 變紅，提醒該 /compact 或 /clear
if   [ "$PCT" -ge 85 ]; then C='\033[31m'
elif [ "$PCT" -ge 70 ]; then C='\033[33m'
else C='\033[32m'; fi
R='\033[0m'
LINE=$(printf "[%s] ${C}ctx %s%%${R} | \$%.2f | %s" "$MODEL" "$PCT" "$COST" "${DIR##*/}")
[ -n "$RL" ] && LINE="$LINE | 5h ${RL}%"
echo -e "$LINE"
