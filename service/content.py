"""内容创作服务"""

import json
import asyncio
import threading
from util.loading import ai_loading
from util.json_util import extract_json
from util.console import print_ai_response, print_success, print_warning, console
from util.txt_util import add_subject
from ai_client import create_client


async def topic_discussion(client):
    """选题探讨"""
    response = await ai_loading(client.chat_history("""我们一起来为易标AI生成自媒体推广选题工作。
                                                     易标AI是一款用AI生成投标技术方案的工具，具备智能解析招标文件、快速生成投标文件、标书查重等功能。
                                                     你需要联网搜索关于AI写标书和易标AI的相关资料，生成5个选题。
                                                     选题面向中小企业老板。
                                                     """))
    print_ai_response(response, title="Gemini")
    
    while True:
        command = input("继续对话，或者输入'ok'继续下一步：")
        if command.strip().lower() == "ok":
            break
        if not command.strip():
            print("请输入内容或输入'ok'继续下一步。")
            continue
        response = await ai_loading(client.chat_history(command))
        print_ai_response(response)

async def content_creation(client):
    """内容创作"""
    command = input("请输入选题：")
    response = await ai_loading(client.chat_history(f"""确定选题是：'''{command}'''。
                                                我们来继续设计内容。
                                                内容是要发布到小红书的，这个平台的特点是图文结合，重点在图片，文字只需要配一个简短的标题和一些标签就行。
                                                封面首图用简洁的大字封面最好。
                                                    """))
    print_ai_response(response)
    
    while True:
        command = input("继续对话，或者输入'ok'继续下一步：")
        if command.strip().lower() == "ok":
            break
        if not command.strip():
            print("请输入内容或输入'ok'继续下一步。")
            continue
        response = await ai_loading(client.chat_history(command))
        print_ai_response(response)


async def generate_json(client) -> dict:
    """生成json并返回解析后的对象"""
    response = await ai_loading(client.chat_history(f"""将我们最后确定的内容整理成json格式，以便于使用nano banana pro 生成图片，尽量保留所有内容，格式如下：
                                                   {{
                                                       "title": "标题",
                                                       "tags": ["标签1", "标签2", "标签3"],
                                                       "image_prompt": ["图片1描述", "图片2描述", "图片3描述"]
                                                       "content":"文案"
                                                   }}
                                                    """), "正在整理 JSON...")
    print_ai_response(response, title="生成的 JSON")
    
    try:
        result = extract_json(response)
        # 使用线程启动后台任务（不受 input() 阻塞影响）
        # 注意：不传递 client，因为异步客户端绑定到原事件循环，需要在新线程中创建新实例
        thread = threading.Thread(
            target=_run_summarize_in_thread,
            args=(result,),
            daemon=True
        )
        thread.start()
        print("\n✅ JSON 解析成功")
        return result
    except (ValueError, json.JSONDecodeError) as e:
        print(f"\n❌ JSON 解析失败: {e}")
        return None


def _run_summarize_in_thread(content_json: dict):
    """在新线程中运行异步总结任务"""
    # 抑制 loguru 日志输出（gemini_webapi 使用 loguru）
    from loguru import logger
    logger.remove()  # 移除所有 handler，静默 gemini_webapi 日志
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_summarize_content(content_json))
    finally:
        loop.close()


async def _summarize_content(content_json: dict):
    """后台任务：总结当前内容"""
    console.print("[dim]📝 后台总结任务已启动[/dim]")
    
    try:
        # 在新线程中创建新的 client 实例
        client = create_client()
        summary = await client.chat(
            "以下是自媒体创造的内容，为了以后不重复生成该主题，你需要分析并总结出一个非常简短的主题，"
            "直接返回总结后的主题，除此之外不要返回任何其他内容。内容如下：\n" 
            + json.dumps(content_json, ensure_ascii=False)
        )
        add_subject(summary.strip())
    except Exception:
        pass  # 静默失败
