"""内容创作服务"""

import json
import asyncio
from util.loading import show_loading
from util.json_util import extract_json
from util.console import print_markdown, print_ai_response


async def topic_discussion(client):
    """选题探讨"""
    task = asyncio.create_task(client.chat_history("""我们一起来为易标AI生成自媒体推广选题工作。
                                                     易标AI是一款用AI生成投标技术方案的工具，具备智能解析招标文件、快速生成投标文件、标书查重等功能。
                                                     你需要联网搜索关于AI写标书和易标AI的相关资料，生成5个选题。
                                                     选题面向中小企业老板。
                                                     """))
    response = await show_loading(task)
    print_ai_response(response, title="Gemini")
    
    while True:
        command = input("继续对话，或者输入'ok'继续下一步：")
        if command.strip().lower() == "ok":
            break
        if not command.strip():
            print("请输入内容或输入'ok'继续下一步。")
            continue
        task = asyncio.create_task(client.chat_history(command))
        response = await show_loading(task)
        print(response)

async def content_creation(client):
    """内容创作"""
    command = input("请输入选题：")
    task = asyncio.create_task(client.chat_history(f"""确定选题是：'''{command}'''。
                                                我们来继续设计内容。
                                                内容是要发布到小红书的，这个平台的特点是图文结合，重点在图片，文字只需要配一个简短的标题和一些标签就行。
                                                封面首图用简洁的大字封面最好。

                                                    """))
    response = await show_loading(task)
    print(response)
    while True:
        command = input("继续对话，或者输入'ok'继续下一步：")
        if command.strip().lower() == "ok":
            break
        if not command.strip():
            print("请输入内容或输入'ok'继续下一步。")
            continue
        task = asyncio.create_task(client.chat_history(command))
        response = await show_loading(task)
        print(response)
    '''
                                                     
                                                   '''
async def generate_json(client) -> dict:
    """生成json并返回解析后的对象"""
    task = asyncio.create_task(client.chat_history(f"""将我们最后确定的内容整理成json格式，以便于使用nano banana pro 生成图片，尽量保留所有内容，格式如下：
                                                   {{
                                                       "title": "标题",
                                                       "tags": ["标签1", "标签2", "标签3"],
                                                       "image_prompt": ["图片1描述", "图片2描述", "图片3描述"]
                                                       "content":"文案"
                                                   }}
                                                    """))
    response = await show_loading(task)
    print(response)
    
    try:
        result = extract_json(response)
        print("\n✅ JSON 解析成功")
        return result
    except (ValueError, json.JSONDecodeError) as e:
        print(f"\n❌ JSON 解析失败: {e}")
        return None
