"""實作 2 用：同一份測試集，比較多個 Prompt 版本與兩家模型。

用法：
  python3 compare.py --task A                      # 預設 v1–v3 × claude、openai，各跑 1 次
  python3 compare.py --task A --runs 2             # 每個組合跑 2 次，觀察穩定度
  python3 compare.py --task C --providers claude   # 只跑 Claude

讀取 prompts/<task>/v*.txt 與 cases/cases_<task>.json，
結果表格印在畫面上，並把失敗題目明細寫到 results/<task>_<時間>.md。

與 eval.py 的差異：
- 比對前移除空白並把全形數字轉半形（「7 天」「7天」「７天」視為相同）
- 支援 must_not_include：輸出中出現任一字串即判定失敗
"""
import argparse, glob, json, os, time
from llm import call

FW = str.maketrans("０１２３４５６７８９", "0123456789")


def norm(s: str) -> str:
    return "".join(s.split()).translate(FW)


def check(text: str, case: dict) -> tuple[bool, str]:
    t = norm(text)
    miss = [k for k in case.get("must_include", []) if norm(k) not in t]
    bad = [k for k in case.get("must_not_include", []) if norm(k) in t]
    reason = ""
    if miss:
        reason += f"缺少：{'、'.join(miss)} "
    if bad:
        reason += f"不應出現：{'、'.join(bad)}"
    return (not miss and not bad), reason.strip()


p = argparse.ArgumentParser()
p.add_argument("--task", required=True, choices=["A", "B", "C"])
p.add_argument("--providers", default="claude,openai")
p.add_argument("--runs", type=int, default=1)
a = p.parse_args()

prompts = sorted(glob.glob(f"prompts/{a.task}/v*.txt"))
cases = json.load(open(f"cases/cases_{a.task}.json", encoding="utf-8"))
providers = a.providers.split(",")
os.makedirs("results", exist_ok=True)

table, fails = {}, []
for pf in prompts:
    ver = os.path.basename(pf)[:-4]
    system = open(pf, encoding="utf-8").read()
    for prov in providers:
        scores = []
        for run in range(a.runs):
            passed = 0
            for c in cases:
                try:
                    out = call(prov, system, c["input"])
                    ok, why = check(out, c)
                except Exception as e:  # 單題失敗不中斷整批
                    out, ok, why = "", False, f"呼叫錯誤：{e}"
                passed += ok
                if not ok:
                    fails.append((ver, prov, run + 1, c["id"], c.get("tag", ""), why, out[:300]))
            scores.append(passed)
        table[(ver, prov)] = scores
        print(f"{ver:>3} {prov:<7} {scores} / {len(cases)}")

n = len(cases)
lines = [f"# 任務 {a.task} 比較結果（{time.strftime('%Y-%m-%d %H:%M')}）", "",
         "| 版本 | " + " | ".join(providers) + " |", "|---|" + "---|" * len(providers)]
for pf in prompts:
    ver = os.path.basename(pf)[:-4]
    lines.append(f"| {ver} | " + " | ".join(
        "、".join(f"{s}/{n}" for s in table[(ver, p)]) for p in providers) + " |")
tags = sorted({c.get("tag", "") for c in cases})
lines += ["", "## 失敗明細", "", "| 版本 | 模型 | 第幾次 | 題號 | 類型 | 原因 | 輸出（前 300 字） |", "|---|---|---|---|---|---|---|"]
for f in fails:
    lines.append("| " + " | ".join(str(x).replace("|", "／").replace("\n", " ") for x in f) + " |")
path = f"results/{a.task}_{time.strftime('%Y%m%d_%H%M%S')}.md"
open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines[:4 + len(prompts)]))
print(f"\n題目類型：{'、'.join(tags)}")
print(f"失敗明細已寫入 {path}")
