"""Gemini 反代实现 (gemini_webapi)"""

from gemini_webapi import GeminiClient
from .base import AIClient


class GeminiWebClient(AIClient):
    """Gemini 反代实现 (gemini_webapi)"""
    
    def __init__(self, secure_1psid: str, secure_1psidts: str = None):
        self.secure_1psid = secure_1psid
        self.secure_1psidts = secure_1psidts
        self.client = None
    
    async def _ensure_client(self):
        if self.client is None:
            self.client = GeminiClient(self.secure_1psid, self.secure_1psidts)
            await self.client.init(auto_refresh=True)
    
    async def chat(self, message: str) -> str:
        await self._ensure_client()
        response = await self.client.generate_content(message, model="gemini-3.0-pro")
        return response.text

