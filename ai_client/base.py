"""AI 请求接口"""

from abc import ABC, abstractmethod


class AIClient(ABC):
    """AI 请求接口"""
    
    @abstractmethod
    async def chat(self, message: str) -> str:
        """单次对话，不保留历史记录"""
        pass
    
    @abstractmethod
    async def chat_history(self, message: str) -> str:
        """多轮对话，保留历史记录"""
        pass
    
    @abstractmethod
    async def image_history(self, message: str) -> str:
        """生成图片，保留历史记录"""
        pass
    
    @abstractmethod
    def reset_chat(self):
        """重置对话历史"""
        pass
