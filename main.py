import asyncio
import time
from dotenv import load_dotenv
from ai_client import create_client
from util.loading import show_loading
from service.content import topic_discussion, content_creation, generate_json
from service.image import generate_images, re_generate_images
from service.publish import publish_content as publish_content_mcp  # MCP 版本备用
from service.publish_xiaohongshu import publish_content as publish_xiaohongshu  # Playwright 版本
from service.publish_douyin import publish_content as publish_douyin
from service.publish_weixin import publish_content as publish_weixin
from util.json_util import save_json, load_json

load_dotenv()


async def main():
    client = create_client()
    content_json = None
    file_path = f"output/{time.strftime('%Y%m%d%H%M%S')}"
 # 测试用
    # file_path = "output/20260105095543"
    # content_json = load_json(file_path)
    
    while True:
        print("""
1. 创建内容
2. 生成图片
3. 发布
4. 退出
              """)
        command = input("请输入命令: ")
        match command:
            case "1":
                while True:
                    print("""
1. 选题探讨
2. 内容创作
3. 生成json
0. 返回上级
                          """)
                    command = input("请输入命令: ")
                    match command:
                        case "1":
                            await topic_discussion(client)
                        case "2":
                            await content_creation(client)
                        case "3":
                            content_json = await generate_json(client)
                            save_json(content_json, file_path)
                        case "0":
                            break
                        case _:
                            print("无效命令")

            case "2":
                content_json = load_json(file_path)
                await generate_images(client, content_json, file_path)
                while True:
                    print("您对那张图片不满意？可以修改content.json中的image_prompt，然后重新生成图片")
                    command = input("请输入图片序号，或者输入OK继续下一步: ")
                    match command:
                        case command if command.isdigit():
                            content_json = load_json(file_path)
                            await re_generate_images(client, content_json, file_path, int(command))
                        case "OK":
                            break
                        case _:
                            print("无效命令，请输入图片序号，或者输入OK继续下一步")
            case "3":
                while True:
                    print("""
1. 发布小红书
2. 发布抖音
3. 发布视频号
0. 返回上级
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
                            print("无效命令")
            case "4":
                print("退出")
                break
            case _:
                print("无效命令")


if __name__ == "__main__":
    asyncio.run(main())
