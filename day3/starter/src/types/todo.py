"""types 層：資料型別與純函式驗證。不可依賴其他層。"""
from dataclasses import dataclass, asdict
from typing import Optional

MAX_TITLE_LENGTH = 200


@dataclass
class Todo:
    id: int
    title: str
    done: bool = False
    due: Optional[str] = None  # YYYY-MM-DD，沒有截止日期時為 None

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Todo":
        return Todo(
            id=int(data["id"]),
            title=str(data["title"]),
            done=bool(data.get("done", False)),
            due=data.get("due"),
        )


def validate_title(title: str) -> Optional[str]:
    """標題合法時回傳 None，不合法時回傳錯誤訊息。"""
    if not isinstance(title, str) or not title.strip():
        return "標題不可空白"
    if len(title.strip()) > MAX_TITLE_LENGTH:
        return f"標題不可超過 {MAX_TITLE_LENGTH} 字"
    return None
