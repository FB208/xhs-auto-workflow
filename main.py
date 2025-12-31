import asyncio
from dotenv import load_dotenv
from ai_client import create_client
from util.loading import show_loading

load_dotenv()


async def main():
    client = create_client()
    
    while True:
        print("""
              1. 创建内容
              2. 生成图片
              3. 发布小红书
              4. 退出
              """)
        command = input("请输入命令: ")
        match command:
            case "1":
                while True:
                    print("""
                          1. 选题探讨
                          2. 内容创作
                          0. 返回上级
                          """)
                    command = input("请输入命令: ")
                    match command:
                        case "1":
                            task = asyncio.create_task(client.chat_history("""我们一起来为易标AI生成自媒体推广选题工作。
                                                                 易标AI是一款用AI生成投标技术方案的工具，具备智能解析招标文件、快速生成投标文件、标书查重等功能。
                                                                 你需要联网搜索关于AI写标书和易标AI的相关资料，生成5个选题。
                                                                 选题面向中小企业老板。
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
                        case "2":
                            print("内容创作")
                        case "0":
                            break
                        case _:
                            print("无效命令")

            case "2":
                message = input("请输入消息: ")
                task = asyncio.create_task(client.chat(message))
                response = await show_loading(task)
                print(response)
            case "3":
                message = input("请输入消息: ")
                task = asyncio.create_task(client.chat(message))
                response = await show_loading(task)
                print(response)
            case "4":
                break
            case _:
                print("无效命令")


if __name__ == "__main__":
    asyncio.run(main())
