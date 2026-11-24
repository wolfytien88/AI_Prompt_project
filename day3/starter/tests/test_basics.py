import tempfile
import unittest
import pathlib

from src.repo.todo_repo import JsonTodoRepo
from src.service.todo_service import TodoService
from src.types.todo import Todo, validate_title, MAX_TITLE_LENGTH


class TestTypes(unittest.TestCase):
    def test_validate_title(self):
        self.assertIsNone(validate_title("買牛奶"))
        self.assertEqual(validate_title("   "), "標題不可空白")
        self.assertIsNotNone(validate_title("字" * (MAX_TITLE_LENGTH + 1)))


class TestRepoAndService(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.tmp.name) / "todos.json"
        self.repo = JsonTodoRepo(str(self.path))

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_list_when_no_file(self):
        self.assertEqual(TodoService(self.repo).list_todos(), [])

    def test_save_and_load_roundtrip(self):
        self.repo.save([Todo(id=1, title="寫報告", due="2026-12-31")])
        loaded = self.repo.load()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].title, "寫報告")
        self.assertEqual(loaded[0].due, "2026-12-31")


if __name__ == "__main__":
    unittest.main()
