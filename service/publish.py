"""小红书发布服务 - 通过 xiaohongshu-mcp
文档: https://github.com/xpzouying/xiaohongshu-mcp
"""

import os
import base64
import httpx
from PIL import Image
import io

MCP_BASE_URL = os.getenv("XHS_MCP_URL", "http://localhost:18060")


async def health_check():
    """健康检查"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{MCP_BASE_URL}/health")
            result = response.json()
            status = result.get("data", {}).get("status", "unknown")
            print(f"🏥 服务状态: {status}")
            return result
        except httpx.HTTPError as e:
            print(f"❌ 健康检查失败: {e}")
            return None


async def check_login():
    """检查登录状态"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{MCP_BASE_URL}/api/v1/login/status")
            result = response.json()
            is_logged_in = result.get("data", {}).get("is_logged_in", False)
            if is_logged_in:
                print("✅ 已登录")
            else:
                print("❌ 未登录")
            return is_logged_in
        except httpx.HTTPError as e:
            print(f"❌ 检查登录状态失败: {e}")
            return False


async def get_qrcode():
    """获取登录二维码并显示"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{MCP_BASE_URL}/api/v1/login/qrcode")
            data = response.json()
            
            # 解码并显示二维码
            img_base64 = data.get("data", {}).get("img", "")
            img_data = base64.b64decode(img_base64.replace("data:image/png;base64,", ""))
            img = Image.open(io.BytesIO(img_data))
            img.show()
            
            timeout = data.get("data", {}).get("timeout", "未知")
            print(f"📱 请在 {timeout} 内扫码登录")
            return True
        except Exception as e:
            print(f"❌ 获取二维码失败: {e}")
            return False


async def login():
    """登录小红书（显示二维码扫码）"""
    is_logged_in = await check_login()
    if is_logged_in:
        print("已经登录，无需重复登录")
        return True
    
    print("🔐 正在获取登录二维码...")
    return await get_qrcode()


async def publish_post(title: str, content: str, images: list[str]):
    """发布小红书图文
    
    参数:
        title: 笔记标题
        content: 笔记内容（包含标签和文案）
        images: 图片URL列表
    
    返回:
        发布结果
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            data = {
                "title": title,
                "content": content,
                "images": images
            }
            
            print(f"📝 正在发布笔记: {title}")
            response = await client.post(
                f"{MCP_BASE_URL}/api/v1/publish",
                json=data
            )
            result = response.json()
            
            if result.get("success"):
                print("✅ 发布成功!")
            else:
                print(f"❌ 发布失败: {result}")
            
            return result
        except httpx.HTTPError as e:
            print(f"❌ 发布请求失败: {e}")
            return None


async def search_content(keyword: str):
    """搜索内容"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{MCP_BASE_URL}/api/v1/search",
                json={"keyword": keyword}
            )
            return response.json()
        except httpx.HTTPError as e:
            print(f"❌ 搜索失败: {e}")
            return None


async def publish_from_json(content_json: dict):
    """从 content_json 发布到小红书
    
    参数:
        content_json: 内容数据，格式如下：
            {
                "title": "标题",
                "tags": ["标签1", "标签2"],
                "image_prompt": ["图片1描述", "图片2描述"],
                "content": "文案",
                "images": ["https://xxx.com/1.png", "https://xxx.com/2.png"]
            }
    
    返回:
        成功返回发布结果，失败返回 None
    """
    if not content_json:
        print("❌ 没有内容可发布，请先创建内容")
        return None
    
    images = content_json.get("images", [])
    if not images:
        print("❌ 没有图片链接，请先生成并上传图片")
        return None
    
    title = content_json.get("title", "")
    tags = content_json.get("tags", [])
    content_text = content_json.get("content", "")
    
    # 组合标签和文案到内容
    tag_text = " ".join(tags) if tags else ""
    full_content = f"{content_text}\n\n{tag_text}".strip()
    
    return await publish_post(title, full_content, images)


async def publish_content(content_json: dict, file_path: str = None, load_json_func=None):
    """完整的发布流程：检查登录 + 校验内容 + 发布
    
    参数:
        content_json: 内容数据
        file_path: 文件路径（用于加载 content.json）
        load_json_func: 加载 JSON 的函数
    
    返回:
        成功返回 True，失败返回 False
    """
    # 检查登录状态
    is_logged_in = await check_login()
    
    if not is_logged_in:
        # 未登录，显示二维码
        await login()
        input("扫码登录后，按回车继续...")
        
        # 再次检查登录状态
        is_logged_in = await check_login()
        if not is_logged_in:
            print("❌ 登录失败，请重试")
            return False
    
    # 尝试加载内容
    if not content_json and file_path and load_json_func:
        content_json = load_json_func(file_path)
    
    # 发布
    result = await publish_from_json(content_json)
    
    if result and result.get("success"):
        print("🎉 发布成功!")
        return True
    
    return False
