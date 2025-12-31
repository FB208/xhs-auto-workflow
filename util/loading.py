"""加载动画工具"""

import sys
import asyncio


async def show_loading(task):
    """显示加载动画直到任务完成
    
    使用方法:
        task = asyncio.create_task(client.chat_history("你好"))
        response = await show_loading(task)
        print(response)
    
    参数:
        task: asyncio.Task 对象
    
    返回:
        task 的执行结果
    """
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while not task.done():
        sys.stdout.write(f"\r{chars[i % len(chars)]} 正在生成请稍后...")
        sys.stdout.flush()
        i += 1
        await asyncio.sleep(0.1)
    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()
    return task.result()

