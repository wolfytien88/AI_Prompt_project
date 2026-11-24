"""edit_tool.py 的測試：python3 -m pytest -q test_edit_tool.py"""
import os
import time

import pytest

import edit_tool
from edit_tool import read_file, edit_file


@pytest.fixture
def sample(tmp_path):
    edit_tool.read_times.clear()
    p = tmp_path / "a.py"
    p.write_text("x = 1\ny = 2\n", encoding="utf-8")
    return str(p)


def bump_mtime(path):
    """模擬外部修改：寫入內容並確保修改時間確實改變。"""
    before = os.path.getmtime(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write("z = 3\n")
    os.utime(path, (before + 5, before + 5))


def test_edit_without_read_is_rejected(sample):
    assert edit_file(sample, "x = 1", "x = 10").startswith("錯誤：檔案在上次讀取後被修改過")


def test_edit_after_read_succeeds(sample):
    read_file(sample)
    assert edit_file(sample, "x = 1", "x = 10") == "已修改"
    assert "x = 10" in open(sample, encoding="utf-8").read()


def test_consecutive_edits_after_own_write(sample):
    read_file(sample)
    assert edit_file(sample, "x = 1", "x = 10") == "已修改"
    assert edit_file(sample, "x = 10", "x = 11") == "已修改"


def test_external_change_is_rejected(sample):
    read_file(sample)
    bump_mtime(sample)
    assert edit_file(sample, "x = 1", "x = 10").startswith("錯誤：檔案在上次讀取後被修改過")
    assert "x = 1\n" in open(sample, encoding="utf-8").read()   # 檔案沒有被覆蓋


def test_old_must_be_unique(sample):
    read_file(sample)
    assert edit_file(sample, "= ", "== ") == "錯誤：old 必須在檔案中剛好出現一次"


def test_old_not_found(sample):
    read_file(sample)
    assert edit_file(sample, "not here", "x") == "錯誤：old 必須在檔案中剛好出現一次"
