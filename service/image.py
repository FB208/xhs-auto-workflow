"""图片生成服务"""

import os
import json
import asyncio
import glob
from util.loading import show_loading
from util.piclist_client import upload_by_path


async def generate_images(client, content_json: dict, file_path: str):
    """根据 content_json 生成图片，上传并更新 content.json
    
    content_json 结构:
        {
            "title": "标题",
            "tags": ["标签1", "标签2", "标签3"],
            "image_prompt": ["图片1描述", "图片2描述", "图片3描述"]
            "content":"文案"
        }
    
    生成完成后会:
        1. 上传 file_path 下所有 png 图片
        2. 将图片链接存入 file_path/content.json 的 images 字段
    """
    if not content_json or "image_prompt" not in content_json:
        print("❌ content_json 无效或缺少 content 字段")
        return []
    
    contents = content_json["image_prompt"]
    
    client.reset_chat()
    
    # 生成图片
    for i, item in enumerate(contents, 1):
        print(f"\n🎨 正在生成第 {i}/{len(contents)} 张图片...")
        task = asyncio.create_task(client.image_history(f"开始生成第{i}张图片，要求宽高比3:4,适合发布到小红书的风格，描述：\n{item}", file_path))
        response = await show_loading(task)
        print(response)
    
    # 上传图片
    print("\n📤 正在上传图片...")
    png_files = sorted(glob.glob(os.path.join(file_path, "*.png")))
    
    if not png_files:
        print("❌ 未找到 png 图片")
        return []
    
    # PicList 需要绝对路径
    abs_png_files = [os.path.abspath(f) for f in png_files]
    print(f"找到 {len(abs_png_files)} 张图片: {[os.path.basename(f) for f in abs_png_files]}")
    
    # 上传到图床
    image_urls = await upload_by_path(abs_png_files)
    
    if image_urls:
        # 更新 content.json
        content_json["images"] = image_urls
        
        json_path = os.path.join(file_path, "content.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(content_json, f, ensure_ascii=False, indent=2)
        
        print(f"✅ content.json 已更新，添加 {len(image_urls)} 个图片链接")
    
    return image_urls
