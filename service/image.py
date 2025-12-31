"""图片生成服务"""

import asyncio
from util.loading import show_loading


async def generate_images(client, content_json: dict, file_path: str):
    """根据 content_json 生成图片
    
    content_json 结构:
        {
            "title": "标题",
            "tags": ["标签1", "标签2", "标签3"],
            "content": ["图片1描述", "图片2描述", "图片3描述"]
        }
    """
    if not content_json or "content" not in content_json:
        print("❌ content_json 无效或缺少 content 字段")
        return []
    
    contents = content_json["content"]
    
    client.reset_chat()
    
    for i, item in enumerate(contents, 1):
        print(f"\n🎨 正在生成第 {i}/{len(contents)} 张图片...")
        task = asyncio.create_task(client.image_history(f"开始生成第{i}张图片，要求宽高比3:4,适合发布到小红书的风格，描述：\n{item}", file_path))
        response = await show_loading(task)
        print(response)
