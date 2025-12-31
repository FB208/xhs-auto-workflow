import os
from http.cookies import SimpleCookie
from .base import AIClient
from .openai_client import OpenAIClient
from .gemini_client import GeminiWebClient


def parse_cookie(cookie_str: str) -> dict:
    """从 cookie 字符串中解析键值对"""
    cookie = SimpleCookie()
    cookie.load(cookie_str)
    return {key: morsel.value for key, morsel in cookie.items()}


def create_client() -> AIClient:
    """根据环境变量配置创建 AI 客户端"""
    provider = os.getenv("AI_PROVIDER", "openai").lower()
    
    if provider == "openai":
        return OpenAIClient(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        )
    elif provider == "gemini":
        cookie_str = os.getenv("GEMINI_COOKIE", "")
        cookies = parse_cookie(cookie_str)
        return GeminiWebClient(
            secure_1psid=cookies.get("__Secure-1PSID"),
            secure_1psidts=cookies.get("__Secure-1PSIDTS")
        )
    else:
        raise ValueError(f"不支持的 AI 提供商: {provider}")


__all__ = ["AIClient", "OpenAIClient", "GeminiWebClient", "create_client"]
