"""AI 请求接口"""

from abc import ABC, abstractmethod


class AIClient(ABC):
    """AI 请求接口"""
    
    @abstractmethod
    async def chat(self, message: str) -> str:
        """发送消息并获取回复"""
        pass

