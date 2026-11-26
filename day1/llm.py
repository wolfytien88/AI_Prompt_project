"""兩家模型的最小呼叫介面：call(provider, system, user) -> 文字。

模型名稱可用環境變數覆寫：CLAUDE_MODEL、OPENAI_MODEL。
沒有 API Key 時，可先啟動 mock/mock_api.py 並設定 *_BASE_URL 離線測試流程。
"""
import os

CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")

_clients = {}


def _claude():
    if "claude" not in _clients:
        import anthropic
        if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("ANTHROPIC_AUTH_TOKEN"):
            raise RuntimeError(
                "未設定 Claude API 憑證。請先設定 ANTHROPIC_API_KEY，"
                "或啟動 Mock 並設定 ANTHROPIC_API_KEY=x。"
            )
        _clients["claude"] = anthropic.Anthropic()
    return _clients["claude"]


def _openai():
    if "openai" not in _clients:
        from openai import OpenAI
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError(
                "未設定 OpenAI API 憑證。請先設定 OPENAI_API_KEY，"
                "或啟動 Mock 並設定 OPENAI_API_KEY=x。"
            )
        _clients["openai"] = OpenAI()
    return _clients["openai"]


def call(provider: str, system: str, user: str, max_tokens: int = 1024) -> str:
    if provider == "claude":
        r = _claude().messages.create(
            model=CLAUDE_MODEL, max_tokens=max_tokens, system=system,
            messages=[{"role": "user", "content": user}],
        )
        # 只取文字區塊；開啟 extended thinking 時第一個區塊會是思考內容
        return "".join(b.text for b in r.content if b.type == "text")
    if provider == "openai":
        r = _openai().responses.create(model=OPENAI_MODEL, instructions=system, input=user)
        return r.output_text
    raise ValueError(f"未知的 provider：{provider}（請用 claude 或 openai）")
