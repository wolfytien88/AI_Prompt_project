#!/usr/bin/env python3
"""把 Claude Code 與 Codex 的非互動輸出彙整成一份 CSV。

輸入（可混合多個檔案）：
  - Claude Code：claude -p ... --output-format json 的輸出（一個 JSON 物件），
    或 --output-format stream-json --verbose 的輸出（每行一個 JSON，取 type=result 那行）
  - Codex：codex exec --json 的輸出（JSONL，取每個 turn.completed 的 usage）

Claude Code 直接回報 total_cost_usd；Codex 只回報 token，費用要用 prices.toml 的單價估算。
prices.toml 的單價請依你的合約或官方價目表填寫，留 0 表示不估算。

用法：
  python3 cost_log.py logs/*.json logs/*.jsonl --codex-model gpt-6.1-sol -o costs.csv
"""
import argparse, csv, json, os, sys

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    tomllib = None

FIELDS = ["tool", "file", "session", "model", "turns", "input_tokens", "cached_input_tokens",
          "cache_write_tokens", "output_tokens", "reasoning_tokens", "cost_usd", "cost_source"]


def load_prices(path):
    if not path or not os.path.exists(path) or tomllib is None:
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f).get("codex", {})


def claude_row(obj, fname):
    u = obj.get("usage") or {}
    models = list((obj.get("modelUsage") or {}).keys())
    return {
        "tool": "claude", "file": fname, "session": obj.get("session_id"),
        "model": "+".join(models) or "?", "turns": obj.get("num_turns"),
        "input_tokens": u.get("input_tokens", 0),
        "cached_input_tokens": u.get("cache_read_input_tokens", 0),
        "cache_write_tokens": u.get("cache_creation_input_tokens", 0),
        "output_tokens": u.get("output_tokens", 0),
        "reasoning_tokens": (u.get("output_tokens_details") or {}).get("thinking_tokens", 0),
        "cost_usd": round(obj.get("total_cost_usd") or 0, 6), "cost_source": "reported",
    }


def codex_row(usage, thread, turns, fname, model, prices):
    p = prices.get(model) or prices.get("default") or {}
    if not any(float(v or 0) for v in p.values()):
        p = {}  # 單價全是 0：只列 token
    per_m = lambda k: float(p.get(k, 0) or 0) / 1_000_000
    inp, cached = usage.get("input_tokens", 0), usage.get("cached_input_tokens", 0)
    out = usage.get("output_tokens", 0)
    cost = (inp - cached) * per_m("input") + cached * per_m("cached_input") + out * per_m("output")
    return {
        "tool": "codex", "file": fname, "session": thread, "model": model, "turns": turns,
        "input_tokens": inp, "cached_input_tokens": cached,
        "cache_write_tokens": usage.get("cache_write_input_tokens", 0),
        "output_tokens": out, "reasoning_tokens": usage.get("reasoning_output_tokens", 0),
        "cost_usd": round(cost, 6) if p else "", "cost_source": "estimated" if p else "tokens-only",
    }


def parse_file(path, model, prices):
    fname = os.path.basename(path)
    text = open(path, encoding="utf-8").read().strip()
    if not text:
        return []
    try:  # 整個檔案是一個 JSON 物件：claude -p --output-format json
        obj = json.loads(text)
        if isinstance(obj, dict) and obj.get("type") == "result":
            return [claude_row(obj, fname)]
    except json.JSONDecodeError:
        pass
    rows, thread, total, turns = [], None, {}, 0
    for line in text.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = ev.get("type")
        if t == "result":                       # Claude stream-json
            rows.append(claude_row(ev, fname))
        elif t == "thread.started":             # Codex
            thread = ev.get("thread_id")
        elif t == "turn.completed":
            turns += 1
            for k, v in (ev.get("usage") or {}).items():
                total[k] = total.get(k, 0) + (v or 0)
    if turns:
        rows.append(codex_row(total, thread, turns, fname, model, prices))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--codex-model", default="default", help="Codex 用的模型名稱（JSON 事件裡沒有）")
    ap.add_argument("--prices", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "prices.toml"))
    ap.add_argument("-o", "--output", default="-")
    a = ap.parse_args()
    prices = load_prices(a.prices)
    rows = [r for f in a.files for r in parse_file(f, a.codex_model, prices)]
    out = sys.stdout if a.output == "-" else open(a.output, "w", newline="", encoding="utf-8")
    w = csv.DictWriter(out, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(rows)
    total = sum(r["cost_usd"] for r in rows if isinstance(r["cost_usd"], (int, float)))
    print(f"共 {len(rows)} 筆，可計算的費用合計 ${total:.4f}", file=sys.stderr)


if __name__ == "__main__":
    main()
