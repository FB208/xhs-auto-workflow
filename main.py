import asyncio
from dotenv import load_dotenv
from ai_client import create_client

load_dotenv()


async def main():
    client = create_client()
    response = await client.chat("你好")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
