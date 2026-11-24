"""檢查 feature_list.json：通過數量，以及需求是否被 Agent 改動。

用法：
  python3 tools/feature_status.py                       # 只顯示通過數
  python3 tools/feature_status.py --save-baseline       # Initializer 完成後執行一次，存下需求快照
  python3 tools/feature_status.py --check-baseline      # 每個 Session 後執行，比對需求有沒有被改

規則：Agent 只能改 passes 欄位。除了 passes 以外的任何變動都會被列出來。
"""
import json
import pathlib
import sys

FEATURES = pathlib.Path("feature_list.json")
BASELINE = pathlib.Path(".feature_baseline.json")


def strip_passes(items):
    return [{k: v for k, v in item.items() if k != "passes"} for item in items]


def main(argv) -> int:
    if not FEATURES.exists():
        print("FAIL 找不到 feature_list.json")
        return 1
    items = json.loads(FEATURES.read_text(encoding="utf-8"))
    passed = sum(1 for i in items if i.get("passes") is True)
    print(f"功能總數 {len(items)}，已通過 {passed}，未通過 {len(items) - passed}")

    if "--save-baseline" in argv:
        BASELINE.write_text(json.dumps(strip_passes(items), ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已存下需求快照：{BASELINE}")
        return 0

    if "--check-baseline" in argv:
        if not BASELINE.exists():
            print("FAIL 沒有需求快照，請先執行 --save-baseline")
            return 1
        base = json.loads(BASELINE.read_text(encoding="utf-8"))
        now = strip_passes(items)
        if len(base) != len(now):
            print(f"FAIL 功能數量從 {len(base)} 變成 {len(now)}：有功能被新增或刪除")
            return 1
        changed = [i for i, (a, b) in enumerate(zip(base, now)) if a != b]
        if changed:
            for i in changed:
                print(f"FAIL 第 {i + 1} 項的需求被改動：{base[i].get('description')}")
            return 1
        print("PASS 需求沒有被改動，只有 passes 欄位有變化")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
