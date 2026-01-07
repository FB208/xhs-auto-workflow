"""抖音发布服务"""

import os
import glob
from util.douyin_client import DouyinClient
from util.console import print_success, print_error, print_info


async def publish_content(content_json: dict, file_path: str = None, load_json_func=None) -> bool:
    """发布图文到抖音"""
    client = DouyinClient(headless=False)
    
    await client.start()
    
    # 检查登录状态
    is_logged_in = await client.check_login()
    
    if not is_logged_in:
        print_info("需要登录抖音...")
        print_info("请在浏览器中完成登录（扫码+验证码），登录成功后按回车继续...")
        
        # 等待用户手动登录（不会刷新页面）
        await client.wait_for_manual_login()
    
    # 尝试加载内容
    if not content_json and file_path and load_json_func:
        content_json = load_json_func(file_path)
    
    if not content_json:
        print_error("没有内容可发布")
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
        print_error("没有找到本地图片，抖音需要本地图片路径")
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
        print_error("抖音内容填写失败，可能未登录或页面有问题")
        print_info("请在浏览器中检查并手动操作，完成后关闭浏览器")
        await client.wait_for_close()
        return False


async def publish_video(video_path: str, title: str, tags: list[str] = None) -> bool:
    """发布视频到抖音"""
    if not os.path.exists(video_path):
        print_error(f"视频文件不存在: {video_path}")
        return False
    
    client = DouyinClient(headless=False)
    
    try:
        await client.start()
        
        is_logged_in = await client.check_login()
        
        if not is_logged_in:
            print_info("需要登录抖音...")
            success = await client.login()
            if not success:
                print_error("登录失败")
                return False
        
        success = await client.upload_video(
            video_path=os.path.abspath(video_path),
            title=title,
            tags=tags
        )
        
        if success:
            print_success("抖音视频发布成功!")
            return True
        else:
            print_error("抖音视频发布失败")
            return False
        
    finally:
        await client.close()
