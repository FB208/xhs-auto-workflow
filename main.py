import asyncio
import time
from dotenv import load_dotenv
from ai_client import create_client
from service.content import topic_discussion, content_creation, generate_json
from service.image import generate_images, re_generate_images, edit_image
from service.publish import publish_content as publish_content_mcp  # MCP 版本备用
from service.publish_xiaohongshu import publish_content as publish_xiaohongshu  # Playwright 版本
from service.publish_douyin import publish_content as publish_douyin
from service.publish_weixin import publish_content as publish_weixin
from util.json_util import save_json, load_json
from util.console import console, print_warning, print_info

load_dotenv()


async def main():
    client = create_client()
    content_json = None
    # file_path = f"output/{time.strftime('%Y%m%d%H%M%S')}"
    # 测试用
    file_path = "output/20260109110444"
    content_json = load_json(file_path)
    
    while True:
        console.print("""
[bold cyan]1.[/] 创建内容
[bold cyan]2.[/] 生成图片
[bold cyan]3.[/] 发布
[bold cyan]4.[/] 从文件加载内容
[bold cyan]0.[/] 退出
        """)
        command = input("请输入命令: ")
        match command:
            case "1":
                while True:
                    console.print("""
[bold cyan]1.[/] 选题探讨
[bold cyan]2.[/] 内容创作
[bold cyan]3.[/] 生成json
[bold cyan]0.[/] 返回上级
                    """)
                    command = input("请输入命令: ")
                    match command:
                        case "1":
                            console.print("""
[bold cyan]1.[/] 易标AI老板视角
[bold cyan]2.[/] 投标人喜欢收藏的内容-不带广
[bold cyan]其他.[/] 不想使用任何预设，不输入序号，直接录入需求即可
                    """)
                            command = input("请输入命令: ")
                            await topic_discussion(client, command)
                        case "2":
                            await content_creation(client)
                        case "3":
                            content_json = await generate_json(client)
                            save_json(content_json, file_path)
                        case "0":
                            break
                        case _:
                            print_warning("无效命令")

            case "2":
                while True:
                    
                    console.print("""
[bold cyan]1.[/] 根据对话结果生成
[bold cyan]2.[/] 修改图片
[bold cyan]0.[/] 返回上级
                        """)
                    command = input("请输入命令: ")
                    match command:
                        case "1":
                            content_json = load_json(file_path)
                            await generate_images(client, content_json, file_path)
                            while True:
                                print_info("您对那张图片不满意？可以修改 content.json 中的 image_prompt，然后重新生成图片")
                                command = input("请输入图片序号，或者输入 ok 继续下一步: ")
                                match command:
                                    case command if command.isdigit():
                                        content_json = load_json(file_path)
                                        await re_generate_images(client, content_json, file_path, int(command))
                                    case "ok":
                                        break
                                    case _:
                                        print_warning("无效命令，请输入图片序号或 ok")
                        case "2":
                            while True:
                                image_index = input("请输入图片序号（初始序号为1）输入0返回上级: ")
                                match image_index:
                                    case "0":
                                        break
                                    case command if command.isdigit():
                                        requirement = input("请输入修改要求: ")
                                        await edit_image(client, file_path, int(image_index), requirement)
                                    case _:
                                        print_warning("无效命令，请输入图片序号或0返回上级")
            case "3":
                while True:
                    console.print("""
[bold cyan]1.[/] 发布小红书
[bold cyan]2.[/] 发布抖音
[bold cyan]3.[/] 发布视频号
[bold cyan]0.[/] 返回上级
                    """)
                    command = input("请输入命令: ")
                    match command:
                        case "1":
                            await publish_xiaohongshu(content_json, file_path, load_json)
                        case "2":
                            await publish_douyin(content_json, file_path, load_json)
                        case "3":
                            await publish_weixin(content_json, file_path, load_json)
                        case "0":
                            break
                        case _:
                            print_warning("无效命令")
            case "4":
                content_json = load_json(file_path)
                console.print(content_json)
            case "0":
                print_info("退出")
                break
            case _:
                print_warning("无效命令")


if __name__ == "__main__":
    asyncio.run(main())
