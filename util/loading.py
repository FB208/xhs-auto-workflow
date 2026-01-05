"""加载动画工具"""

from rich.console import Console

console = Console()


async def ai_loading(coroutine, message: str = "正在生成请稍后..."):
    """显示加载动画直到异步任务完成
    
    使用方法:
        response = await ai_loading(client.chat_history("你好"))
        
        # 自定义提示文字
        response = await ai_loading(client.chat_history("你好"), "思考中...")
    """
    with console.status(f"[bold cyan]{message}[/bold cyan]", spinner="dots"):
        result = await coroutine
    return result
