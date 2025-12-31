"""OpenAI SDK 实现"""

from openai import OpenAI
from .base import AIClient


class OpenAIClient(AIClient):
    """OpenAI SDK 实现"""
    
    def __init__(self, api_key: str, base_url: str = None, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
    
    async def chat(self, message: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content

