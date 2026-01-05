"""图片生成服务"""

import os
import json
import glob
from util.loading import ai_loading
from util.piclist_client import upload_by_path
from util.console import print_success, print_error, print_info


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
        print_error("content_json 无效或缺少 image_prompt 字段")
        return []
    
    contents = content_json["image_prompt"]
    
    client.reset_chat()
    
    # 生成图片
    for i, item in enumerate(contents, 1):
        print_info(f"正在生成第 {i}/{len(contents)} 张图片...")
        response = await ai_loading(
            client.image_history(f"开始生成第{i}张图片，要求宽高比3:4，图片内容：\n{item}", file_path, i),
            f"🎨 生成第 {i}/{len(contents)} 张图片..."
        )
        print_success(f"第 {i} 张图片生成完成")
    
    print_success(f"全部 {len(contents)} 张图片生成完成")


async def re_generate_images(client, content_json: dict, file_path: str, image_index: int):
    """重新生成指定图片"""
    contents = content_json["image_prompt"]
    item = contents[image_index - 1]  # 用户输入从1开始
    
    print_info(f"正在重新生成第 {image_index} 张图片...")
    response = await ai_loading(
        client.image_history(f"开始重新生成第{image_index}张图片，要求宽高比3:4，图片内容：\n{item}", file_path, image_index),
        f"🎨 重新生成第 {image_index} 张图片..."
    )
    print_success(f"第 {image_index} 张图片重新生成完成")
