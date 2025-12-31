"""Redis 客户端"""

import os
import redis


class RedisClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_client()
        return cls._instance
    
    def _init_client(self):
        self.client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            password=os.getenv("REDIS_PASSWORD") or None,
            decode_responses=True
        )
    
    def get(self, key: str) -> str:
        return self.client.get(key)
    
    def set(self, key: str, value: str, ex: int = None) -> bool:
        return self.client.set(key, value, ex=ex)
    
    def delete(self, key: str) -> int:
        return self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        return self.client.exists(key) > 0


def get_redis() -> RedisClient:
    """获取 Redis 客户端单例"""
    return RedisClient()

