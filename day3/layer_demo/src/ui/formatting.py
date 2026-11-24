"""ui 層：畫面顯示用的格式化。"""


def format_title(title: str, done: bool) -> str:
    """完成的項目在標題前加上 [完成]。"""
    return f"[完成] {title}" if done else title


def render_line(title: str, done: bool) -> str:
    return f"<li>{format_title(title, done)}</li>"
