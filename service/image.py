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
    
    image_prompts = content_json["image_prompt"]
    
    client.reset_chat()
    
    # 批量生成
    # image_prompts_str = "\n".join([f"{i+1}. {desc}" for i, desc in enumerate(image_prompts)])
    # prompt = f"""
    # 按照如下提示词，使用nano banana pro分别生成{len(image_prompts)}张图片，每张图片宽高比都是3:4，注意保持风格一致，图片描述如下，不要遗漏：
    # {image_prompts_str}
    # """
    # response = await ai_loading(
    #     client.image_history(prompt, file_path,None),
    #     f"🎨 正在批量生成图片"
    # )
    # print_success(f"封面首图生成完成")
    
    # 单条生成
    # response = await ai_loading(
    #         client.image_history(f"帮我用nano banana pro生成图片，每张图片的宽高比都是3:4，注意保持风格一致，你准备好了吗？", file_path, None),
    #         f"🎨 正在准备生成图片..."
    #     )
    # print_success(f"response")
    for i, item in enumerate(image_prompts, 1):
        print_info(f"正在生成第 {i}/{len(image_prompts)} 张图片...")
        response = await ai_loading(
            client.image_history(f"开始生成第{i}张图片，要求宽高比3:4，图片内容：\n{item}", file_path, i),
            f"🎨 生成第 {i}/{len(image_prompts)} 张图片..."
        )
        print_success(f"第 {i} 张图片生成完成")
    
    print_success(f"全部 {len(image_prompts)} 张图片生成完成")


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
    
async def edit_image(client,file_path: str,image_index: str,requirement: str):
    """编辑图片"""
    client.reset_chat()
    image_path = os.path.abspath(os.path.join(file_path, f"{image_index}.png"))
    print_info(f"编辑图片: {image_path}")
    response = await ai_loading(
        client.image(f"{requirement}", file_path, image_index, image_path),
        f"🎨 重新生成第 {image_index} 张图片..."
    )
    print_success(f"第 {image_index} 张图片编辑完成")