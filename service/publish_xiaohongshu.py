"""小红书发布服务 - Playwright 版本"""

import os
import glob
from util.xiaohongshu_client import XiaohongshuClient


async def publish_content(content_json: dict, file_path: str = None, load_json_func=None) -> bool:
    """发布图文到小红书
    
    参数:
        content_json: 内容数据，格式如下：
            {
                "title": "标题",
                "tags": ["标签1", "标签2"],
                "content": "文案",
                "images": ["url1", "url2"]
            }
        file_path: 内容目录路径
        load_json_func: 加载 JSON 的函数
    
    返回:
        成功返回 True，失败返回 False
    """
    client = XiaohongshuClient(headless=False)
    
    await client.start()
    
    # 检查登录状态
    is_logged_in = await client.check_login()
    
    if not is_logged_in:
        print("🔐 需要登录小红书...")
        success = await client.login()
        if not success:
            print("❌ 登录失败")
            print("🔍 请在浏览器中排查问题，关闭浏览器后程序继续...")
            await client.wait_for_close()
            return False
    
    # 尝试加载内容
    if not content_json and file_path and load_json_func:
        content_json = load_json_func(file_path)
    
    if not content_json:
        print("❌ 没有内容可发布")
        await client.close()
        return False
    
    # 获取本地图片路径
    image_paths = []
    if file_path:
        abs_file_path = os.path.abspath(file_path)
        print(f"📁 图片目录: {abs_file_path}")
        png_files = sorted(glob.glob(os.path.join(abs_file_path, "*.png")))
        image_paths = png_files
        print(f"📷 找到 {len(image_paths)} 张图片: {[os.path.basename(f) for f in image_paths]}")
    
    if not image_paths:
        print("❌ 没有找到本地图片")
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
        # 等待用户关闭浏览器
        await client.wait_for_close()
        return True
    else:
        print("❌ 小红书内容填写失败")
        print("🔍 请在浏览器中排查问题，关闭浏览器后程序继续...")
        await client.wait_for_close()
        return False

