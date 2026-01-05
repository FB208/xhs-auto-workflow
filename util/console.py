"""终端美化输出工具 - 支持 Markdown 渲染"""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# 全局 Console 实例
console = Console()


def print_markdown(text: str):
    """在终端中渲染 Markdown 文本
    
    用法:
        from util.console import print_markdown
        print_markdown("# 标题\\n- 列表项1\\n- 列表项2")
    """
    md = Markdown(text)
    console.print(md)


def print_ai_response(text: str, title: str = "AI 回复"):
    """美化输出 AI 响应（带边框）
    
    用法:
        from util.console import print_ai_response
        print_ai_response(response, title="Gemini")
    """
    md = Markdown(text)
    panel = Panel(md, title=title, border_style="cyan")
    console.print(panel)


def print_success(text: str):
    """打印成功消息（绿色）"""
    console.print(f"[green]✅ {text}[/green]")


def print_error(text: str):
    """打印错误消息（红色）"""
    console.print(f"[red]❌ {text}[/red]")


def print_warning(text: str):
    """打印警告消息（黄色）"""
    console.print(f"[yellow]⚠️ {text}[/yellow]")


def print_info(text: str):
    """打印信息消息（蓝色）"""
    console.print(f"[blue]ℹ️ {text}[/blue]")

