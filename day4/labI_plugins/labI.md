# 實作 I：把團隊設定打包成外掛

> 在 VS Code 中操作本實作的方式，見 [`../../vscode.md`](../../vscode.md)。

## 目的

- 把散落在各專案的 Skill、Subagent 與 Hook 打包成一個**外掛（plugin）**，再放進**市集（marketplace）**，讓整個團隊用一行指令安裝同一套設定。
- 在 Claude Code 與 Codex 各做一次，找出哪些元件兩邊通用、哪些要各寫一份。
- 了解外掛裡的 Hook 為什麼要另外信任。

## 形式

兩人一組：一人扮演「工具維護者」打包與發布，另一人扮演「新進同仁」安裝與驗證，做完交換。

## 前置

| 項目 | 說明 |
| --- | --- |
| 軟體 | Git、Python 3.10+、Claude Code CLI、Codex CLI 0.165 以上 |
| 教材檔案 | `setup.sh`、`starter/`（散落的 Skill、Subagent、`guard.py`）、`team/`（團隊佈署範本） |
| 先備 | 實作 7 的 `guard.py`（已附在 `starter/hooks/`） |

## 步驟

### 1. 建立練習 repo

```bash
bash <教材路徑>/setup.sh       # 建立 ~/labI/repo（含本機遠端 remote.git 與一筆未提交的變更）
```

`starter/README.md` 列出四個要打包的素材：

- `pr-summary` Skill
- `security-reviewer` Subagent（Claude Code 的 Markdown 版與 Codex 的 TOML 版）
- `guard.py`

### 2. 做出 Claude Code 外掛

建立以下結構：

```
~/labI/acme-marketplace/
├── .claude-plugin/
│   └── marketplace.json
└── plugins/acme-team-kit/
    ├── .claude-plugin/plugin.json      ← 只放清單檔
    ├── skills/pr-summary/SKILL.md
    ├── agents/security-reviewer.md
    └── hooks/
        ├── hooks.json
        └── guard.py
```

`plugin.json`：

```json
{
  "name": "acme-team-kit",
  "description": "Acme 團隊共用工具包",
  "version": "1.0.0",
  "author": { "name": "Acme 研發效能小組" },
  "license": "MIT"
}
```

`hooks/hooks.json`：外掛內的檔案路徑一律用 `${CLAUDE_PLUGIN_ROOT}`，不要寫死。

```json
{"hooks":{"PreToolUse":[{"matcher":"Bash","hooks":[
  {"type":"command","command":"python3 \"${CLAUDE_PLUGIN_ROOT}/hooks/guard.py\"","timeout":30}]}]}}
```

`marketplace.json`：

```json
{
  "name": "acme-tools",
  "description": "Acme 團隊內部外掛市集",
  "owner": { "name": "Acme 研發效能小組" },
  "plugins": [ { "name": "acme-team-kit", "source": "./plugins/acme-team-kit" } ]
}
```

容易出錯的地方：

- `skills/`、`agents/`、`hooks/` 要放在外掛**根目錄**。放進 `.claude-plugin/` 裡不會載入。
- `marketplace.json` 裡的 `name` 必須與 `plugin.json` 的 `name` 相同。
- 同一個 Hook 若同時寫在 `settings.json` 與外掛裡，會執行兩次。

### 3. 驗證與試用（還不用安裝）

```bash
claude plugin validate ~/labI/acme-marketplace/plugins/acme-team-kit
claude plugin validate ~/labI/acme-marketplace
cd ~/labI/repo
claude --plugin-dir ~/labI/acme-marketplace/plugins/acme-team-kit
```

在對話中試三件事：

1. `/acme-team-kit:pr-summary reviewer`：外掛的 Skill 會加上外掛名稱當前綴。
2. `請用 @agent-acme-team-kit:security-reviewer 審查 util.py`
3. `git add -A && git commit -m wip` 之後，請它 `git push origin main`，應被外掛的 Hook 擋下。

也可以用非互動模式測 Skill：`claude -p "/acme-team-kit:pr-summary reviewer" --plugin-dir <外掛路徑>`

### 4. 從市集安裝

由「新進同仁」操作：

```bash
claude plugin marketplace add ~/labI/acme-marketplace
claude plugin install acme-team-kit@acme-tools
claude plugin details acme-team-kit@acme-tools     # 元件清單與每次對話固定增加的 token
```

互動模式中用 `/plugin` 也能瀏覽與安裝；改了外掛內容後用 `/reload-plugins` 重新載入。

### 5. 讓 Codex 用同一個市集

```bash
export CODEX_HOME=~/labI/codex-home        # 隔離練習設定
codex plugin marketplace add ~/labI/acme-marketplace
codex plugin list
codex plugin add acme-team-kit@acme-tools
```

0.165 實測：Codex 可以直接讀 Claude 格式的 `.claude-plugin/marketplace.json` 與 `plugin.json`。觀察哪些元件生效：

| 元件 | 在 Codex 的情況 |
| --- | --- |
| Skill | 生效，名稱為 `acme-team-kit:pr-summary`，用 `$acme-team-kit:pr-summary` 明確叫用 |
| Hook | 安裝後**不會自動信任**。要在互動模式執行 `/hooks` 審查並信任，才會開始擋 |
| Subagent（Markdown） | 不會載入。Codex 的自訂 Agent 是 `.codex/agents/*.toml`，把 `starter/.codex/agents/security-reviewer.toml` 放進專案 |

接著做 Codex 原生格式：把清單檔改放在 `plugins/acme-team-kit/.codex-plugin/plugin.json`，市集清單放在 `.agents/plugins/marketplace.json`，用 `codex plugin marketplace add` 加入，確認兩種格式都能安裝。

### 6. 確認 Hook 信任

```bash
cd ~/labI/repo
codex                  # 互動模式
```

1. 在互動模式中請它 `git push origin main`。Hook 尚未信任時，推送會成功。
2. 輸入 `/hooks`，信任 `acme-team-kit` 的 PreToolUse Hook。
3. 重新要求推送，這次應被擋下，訊息是「禁止直接推送到 main，請開 PR」。

討論：為什麼安裝外掛不等於信任它的 Hook？如果外掛更新後 Hook 的內容變了，會發生什麼事？Hook 信任綁定內容的雜湊值，內容改變後要重新信任。

### 7. 佈署給整個團隊

**Claude Code**：把下列設定提交到專案的 `.claude/settings.json`。同仁第一次在這個資料夾開啟 Claude Code 並同意信任資料夾後，會被提示安裝。

```json
{
  "extraKnownMarketplaces": {
    "acme-tools": { "source": { "source": "github", "repo": "acme-example/claude-plugins" } }
  },
  "enabledPlugins": { "acme-team-kit@acme-tools": true }
}
```

市集放在本機資料夾時，`source` 改成 `{ "source": "directory", "path": "<路徑>" }`（見 `team/claude_settings_local_dir.json`）。

**Codex**：`codex plugin marketplace add` 與 `codex plugin add` 會寫入使用者的 `config.toml`（見 `team/codex_config_snippet.toml`）。目前的做法是請每位同仁各執行一次這兩行指令。

## 觀察重點

- `claude plugin details` 顯示的「Always-on」token 是多少？外掛裝得越多，每次對話的固定成本越高。
- Hook 只在 Codex 被信任後才生效。Claude Code 呢？外掛的 Hook 需要另外信任嗎？
- 哪些元件兩邊可以共用同一份檔案？哪些一定要各寫一份？

## 檢核點

- [ ] `claude plugin validate` 對外掛與市集都回報 `Validation passed`
- [ ] `--plugin-dir` 下，`/acme-team-kit:pr-summary` 與 `@agent-acme-team-kit:security-reviewer` 都能用
- [ ] 外掛的 Hook 在 Claude Code 擋下 `git push origin main`
- [ ] Codex 透過市集安裝成功，信任 Hook 前後的結果不同
- [ ] 寫出團隊佈署用的 `.claude/settings.json`

## 延伸題

1. 在外掛根目錄加一份 `.mcp.json`，打包實作 D 的 MCP 伺服器，再用 `claude plugin details` 看 MCP 伺服器有沒有出現。
2. 用 `claude plugin tag` 為外掛建立版本標籤，再把 `version` 改成 `1.1.0`，練習 `claude plugin update`。
3. 用 `claude plugin validate --strict` 當 CI 檢查，故意加一個不認得的欄位，看它如何失敗。

## 沒有 API 金鑰時

- `claude plugin validate`、`claude plugin marketplace add`、`claude plugin install`、`claude plugin details`、`codex plugin marketplace add`、`codex plugin add`、`codex plugin list` 都不呼叫模型。
- 要實際觸發 Skill、Subagent 或 Hook，才需要模型。講師可用 `instructor/verify_codex_plugin.sh` 以模擬模型示範 Codex 的 Hook 信任差異。

## 兩邊比較

| 面向 | Claude Code | Codex |
|---|---|---|
| 外掛清單檔 | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json`（實測也接受 `.claude-plugin/`） |
| 市集清單檔 | `.claude-plugin/marketplace.json` | `.agents/plugins/marketplace.json`（實測也接受 Claude 格式） |
| 加市集 | `claude plugin marketplace add <來源>` | `codex plugin marketplace add <來源>` |
| 安裝 | `claude plugin install 名稱@市集` | `codex plugin add 名稱@市集` |
| Skill | 通用，叫用名稱 `外掛:skill` | 通用，叫用名稱 `外掛:skill` |
| Subagent | 外掛的 `agents/*.md` | 不在外掛內；專案 `.codex/agents/*.toml` |
| 外掛的 Hook | 安裝後直接生效 | 需用 `/hooks` 信任，內容改變要重新信任 |
| 團隊佈署 | 專案 `.claude/settings.json`：`extraKnownMarketplaces`＋`enabledPlugins` | 每人 `config.toml`：`[marketplaces.x]`＋`[plugins."名稱@市集"]` |

## 參考

- Claude Code 建立外掛：https://code.claude.com/docs/en/plugins/create
- Claude Code 建立市集：https://code.claude.com/docs/en/plugins/create-marketplace
- Claude Code 設定（extraKnownMarketplaces、enabledPlugins）：https://code.claude.com/docs/en/settings
- Codex Skills 與外掛：https://learn.chatgpt.com/codex/skills-and-plugins
- Codex Hooks（信任流程）：https://learn.chatgpt.com/docs/hooks
- Codex 自訂 Agent：https://learn.chatgpt.com/codex/agent-configuration/subagents
