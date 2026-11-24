#!/usr/bin/env bash
# 講師課前驗證：Codex 沙箱探測（不需要 OpenAI 金鑰，codex sandbox 不呼叫模型）
set -uo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-$HOME/labH}"
bash "$HERE/setup.sh" "$BASE" >/dev/null
export CODEX_HOME="$BASE/codex-home"
echo "== 權限設定檔 lab"; bash "$HERE/codex_probes.sh" "$BASE/proj" lab
echo "== 內建 :workspace（對照）"; bash "$HERE/codex_probes.sh" "$BASE/proj" :workspace
echo "== 拿掉 network_proxy（對照：網域規則失效）"
sed 's/network_proxy = true/network_proxy = false/' "$CODEX_HOME/config.toml" > "$CODEX_HOME/config.noproxy" && cp "$CODEX_HOME/config.toml" "$CODEX_HOME/config.bak" && cp "$CODEX_HOME/config.noproxy" "$CODEX_HOME/config.toml"
bash "$HERE/codex_probes.sh" "$BASE/proj" lab | grep -E '^P5|^P6'
cp "$CODEX_HOME/config.bak" "$CODEX_HOME/config.toml"
echo "== 已移除的設定"
codex exec --full-auto "hi" </dev/null 2>&1 | head -1
mkdir -p "$BASE/codex-home-untrusted"; printf 'approval_policy = "untrusted"\n' > "$BASE/codex-home-untrusted/config.toml"
CODEX_HOME="$BASE/codex-home-untrusted" codex exec "hi" </dev/null 2>&1 | head -1
