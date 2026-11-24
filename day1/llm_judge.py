"""LLM-as-judge 範例：先產生回覆，再用「獨立的呼叫」評分。

用法：
  python3 llm_judge.py --prompt prompts/A/v2.txt --generator claude --judge openai
  python3 llm_judge.py --prompt prompts/A/v3.txt --generator openai --judge claude --limit 5

重點：
- 生成與評分是兩次獨立呼叫，評分者看不到生成者的推理過程
- 評分標準逐項給分，並要求只輸出 JSON
- 建議用另一家模型評分，再抽 5 題人工評分對照
"""
import argparse, json, re
from pathlib import Path
from llm import call

BASE_DIR = Path(__file__).resolve().parent
JUDGE = """你是嚴格的客服品質稽核員。依下列標準替 <reply> 評分：
1. 符合 <policy>（0–2）
2. 回答了客戶的問題（0–2）
3. 語氣有同理心且專業（0–1）
有任何疑慮就給低分，不要因為文字流暢就給高分。
只輸出 JSON：{"score": 整數, "reason": 字串}"""

p = argparse.ArgumentParser()
p.add_argument("--prompt", required=True)
p.add_argument("--cases", default="cases/cases_A.json")
p.add_argument("--policy", default="data/policy.md")
p.add_argument("--generator", choices=["claude", "openai"], default="claude")
p.add_argument("--judge", choices=["claude", "openai"], default="openai")
p.add_argument("--limit", type=int, default=0, help="只跑前 N 題（0 = 全部）")
a = p.parse_args()


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    return cwd_path if cwd_path.exists() else BASE_DIR / path


prompt_path = resolve_path(a.prompt)
policy_path = resolve_path(a.policy)
cases_path = resolve_path(a.cases)
if not prompt_path.is_file():
    p.error(f"找不到 Prompt 檔案：{a.prompt}")
if not policy_path.is_file():
    p.error(f"找不到規定檔案：{a.policy}")
if not cases_path.is_file():
    p.error(f"找不到測試集檔案：{a.cases}")

system = prompt_path.read_text(encoding="utf-8")
policy = policy_path.read_text(encoding="utf-8")
cases = json.loads(cases_path.read_text(encoding="utf-8"))
if a.limit:
    cases = cases[: a.limit]

scores, errors = [], 0
for c in cases:
    reply = call(a.generator, system, c["input"])
    user = f"<policy>\n{policy}\n</policy>\n<email>\n{c['input']}\n</email>\n<reply>\n{reply}\n</reply>"
    raw = call(a.judge, JUDGE, user, max_tokens=300)
    m = re.search(r"\{.*\}", raw, re.S)
    try:
        r = json.loads(m.group(0)) if m else None
        score, reason = int(r["score"]), r.get("reason", "")
        scores.append(score)
        print(f"{c['id']}  {score}/5  {reason[:60]}")
    except Exception:
        errors += 1
        print(f"{c['id']}  無法解析評分結果：{raw[:60]!r}")

if scores:
    print(f"\n平均 {sum(scores)/len(scores):.2f} / 5（{len(scores)} 題）")
if errors:
    print(f"{errors} 題無法解析，請檢查評分 Prompt 或改用 Structured Outputs")
