"""视频号发布服务"""

import os
import glob
from util.weixin_client import WeixinClient
from util.console import print_success, print_error, print_info


async def publish_content(content_json: dict, file_path: str = None, load_json_func=None) -> bool:
    """发布图文到视频号"""
    client = WeixinClient(headless=False)
    
    await client.start()
    
    # 检查登录状态
    is_logged_in = await client.check_login()
    
    if not is_logged_in:
        print_info("需要登录视频号...")
        success = await client.login()
        if not success:
            print_error("登录失败")
            await client.close()
            return False
    
    # 尝试加载内容
    if not content_json and file_path and load_json_func:
        content_json = load_json_func(file_path)
    
    if not content_json:
        print_error("没有内容可发布")
        await client.close()
        return False
    
    # 获取本地图片路径
    image_paths = []
    if file_path:
        abs_file_path = os.path.abspath(file_path)
        print_info(f"图片目录: {abs_file_path}")
        png_files = sorted(glob.glob(os.path.join(abs_file_path, "*.png")))
        image_paths = png_files
        print_info(f"找到 {len(image_paths)} 张图片")
    
    if not image_paths:
        print_error("没有找到本地图片，视频号需要本地图片路径")
        await client.close()
        return False
    
    # 发布
    title = content_json.get("title", "")
    content = content_json.get("content", "")
    tags = content_json.get("tags", [])
    
    success = await client.upload_images(
        image_paths=image_paths,
        title=title,
        content=content,
        tags=tags
    )
    
    if success:
        await client.wait_for_close()
        return True
    else:
        print_error("视频号内容填写失败")
        print_info("请在浏览器中排查问题，关闭浏览器后程序继续...")
        await client.wait_for_close()
        return False
