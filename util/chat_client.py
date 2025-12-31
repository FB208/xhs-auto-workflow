import asyncio
from ai_client import create_client

async def chat(message: str) -> str:
    client = create_client()
    response = await client.chat(message)
    return response