"""service 層：業務邏輯。可依賴 types 與 repo，不可依賴 ui。"""
from typing import List

from src.repo.todo_repo import JsonTodoRepo
from src.types.todo import Todo


class TodoService:
    def __init__(self, repo: JsonTodoRepo):
        self.repo = repo

    def list_todos(self) -> List[Todo]:
        return self.repo.load()

    # 以下功能尚未實作，由 Coding Agent 依 feature_list.json 逐項完成：
    # 新增、標記完成、刪除、編輯、篩選、清除已完成、截止日期……
