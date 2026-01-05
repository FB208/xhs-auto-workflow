"""Gemini 反代实现 (gemini_webapi)"""

from gemini_webapi import GeminiClient
from .base import AIClient
import time


class GeminiWebClient(AIClient):
    """Gemini 反代实现 (gemini_webapi)"""
    
    def __init__(self, secure_1psid: str, secure_1psidts: str = None):
        self.secure_1psid = secure_1psid
        self.secure_1psidts = secure_1psidts
        self.client = None
        self.chat_session = None
    
    async def _ensure_client(self):
        if self.client is None:
            self.client = GeminiClient(self.secure_1psid, self.secure_1psidts)
            await self.client.init(auto_refresh=True)
    
    async def chat(self, message: str) -> str:
        """单次对话，不保留历史记录"""
        await self._ensure_client()
        response = await self.client.generate_content(message, model="gemini-3.0-pro")
        return response.text
    
    async def chat_history(self, message: str) -> str:
        """多轮对话，保留历史记录"""
        await self._ensure_client()
        
        if self.chat_session is None:
            self.chat_session = self.client.start_chat(model="gemini-3.0-pro")
        
        response = await self.chat_session.send_message(message)
        return response.text
    
    async def image_history(self, message: str, file_path: str,file_name: str) -> str:
        """生成图片，保留历史记录, 保存到 file_path"""
        await self._ensure_client()
        
        if self.chat_session is None:
            self.chat_session = self.client.start_chat(model="gemini-3.0-pro")
        
        response = await self.chat_session.send_message(message)
        for i, image in enumerate(response.images):  
            await image.save(path=file_path, filename=f"{file_name}.png", verbose=True)
        return response.text
    
    def reset_chat(self):
        """重置对话历史，开始新会话"""
        self.chat_session = None
