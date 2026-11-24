"""service 層：產生每日報告。

【故意違規】這支程式為了重用 format_title，直接 import 了 ui 層。
執行 make lint 會失敗；修正方式見 lab6.md 的 Part A。
"""
from typing import List, Tuple

from src.ui.formatting import format_title


def daily_report(items: List[Tuple[str, bool]]) -> str:
    """items 為 (標題, 是否完成) 的清單，回傳純文字報告。"""
    lines = [format_title(title, done) for title, done in items]
    remaining = sum(1 for _, done in items if not done)
    lines.append(f"剩 {remaining} 項")
    return "\n".join(lines)
