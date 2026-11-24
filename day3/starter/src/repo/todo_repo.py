"""repo 層：資料存取。只可依賴 types 層。"""
import json
import pathlib
from typing import List

from src.types.todo import Todo


class JsonTodoRepo:
    """把待辦清單存成一個 JSON 檔。"""

    def __init__(self, path: str):
        self.path = pathlib.Path(path)

    def load(self) -> List[Todo]:
        if not self.path.exists():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return [Todo.from_dict(item) for item in data]

    def save(self, todos: List[Todo]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [t.to_dict() for t in todos]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
