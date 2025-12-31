"""OpenAI SDK 实现"""

from openai import OpenAI
from .base import AIClient


class OpenAIClient(AIClient):
    """OpenAI SDK 实现"""
    
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.history = []
    
    async def chat(self, message: str) -> str:
        """单次对话，不保留历史记录"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content
    
    async def chat_history(self, message: str) -> str:
        """多轮对话，保留历史记录"""
        self.history.append({"role": "user", "content": message})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history
        )
        
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply
    
    def reset_chat(self):
        """重置对话历史"""
        self.history = []
