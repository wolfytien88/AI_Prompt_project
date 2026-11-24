# 審查規則（兩套 Agent 共用）

## P0：必須在合併前修正
- 金額、稅額、折扣計算錯誤
- 未驗證的使用者輸入直接進入 SQL、shell 指令或檔案路徑
- 金鑰、Token、密碼寫進程式或設定檔

## P1：本週內修正
- 錯誤被吞掉（except: pass、空的 catch）
- 新增的公開函式沒有對應測試
- 違反 docs/architecture.md 的分層規則（ui → service → repo → types）

## 不需回報
- 命名、排版、註解措辭等風格問題（交給 linter）
