"""PicList 图床客户端
文档: https://piclist.cn/advanced.html#内置http服务器
"""

import os
import httpx

PICLIST_BASE_URL = os.getenv("PICLIST_URL", "http://127.0.0.1:36677")
PICLIST_KEY = os.getenv("PICLIST_KEY", "")  # 可选的鉴权密钥


def _build_url(endpoint: str) -> str:
    """构建带鉴权的 URL"""
    url = f"{PICLIST_BASE_URL}/{endpoint}"
    if PICLIST_KEY:
        url += f"?key={PICLIST_KEY}"
    return url


async def heartbeat() -> bool:
    """健康检查"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(_build_url("heartbeat"))
            result = response.json()
            if result.get("success") and result.get("result") == "alive":
                print("✅ PicList 服务正常")
                return True
            print("❌ PicList 服务异常")
            return False
        except httpx.HTTPError as e:
            print(f"❌ PicList 连接失败: {e}")
            return False


async def upload_by_path(image_paths: list[str], picbed: str = None, config_name: str = None) -> list[str]:
    """通过本地路径上传图片
    
    参数:
        image_paths: 本地图片路径列表
        picbed: 可选，指定图床类型（如 aws-s3, qiniu, github 等）
        config_name: 可选，指定配置文件名称
    
    返回:
        上传成功后的图片 URL 列表
    
    使用示例:
        urls = await upload_by_path(["D:/images/1.jpg", "D:/images/2.png"])
        print(urls)  # ["https://example.com/1.jpg", "https://example.com/2.png"]
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            url = _build_url("upload")
            
            # 添加可选参数
            params = []
            if picbed:
                params.append(f"picbed={picbed}")
            if config_name:
                params.append(f"configName={config_name}")
            if params:
                separator = "&" if PICLIST_KEY else "?"
                url += separator + "&".join(params)
            
            response = await client.post(
                url,
                json={"list": image_paths},
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            
            if result.get("success"):
                urls = result.get("result", [])
                print(f"✅ 上传成功: {len(urls)} 张图片")
                return urls
            else:
                print(f"❌ 上传失败: {result}")
                return []
        except httpx.HTTPError as e:
            print(f"❌ 上传请求失败: {e}")
            return []


async def upload_by_form(image_path: str, picbed: str = None, config_name: str = None) -> str:
    """通过表单上传单张图片
    
    参数:
        image_path: 本地图片路径
        picbed: 可选，指定图床类型
        config_name: 可选，指定配置文件名称
    
    返回:
        上传成功后的图片 URL
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            url = _build_url("upload")
            
            # 添加可选参数
            params = []
            if picbed:
                params.append(f"picbed={picbed}")
            if config_name:
                params.append(f"configName={config_name}")
            if params:
                separator = "&" if PICLIST_KEY else "?"
                url += separator + "&".join(params)
            
            with open(image_path, "rb") as f:
                files = {"image": (os.path.basename(image_path), f)}
                response = await client.post(url, files=files)
            
            result = response.json()
            
            if result.get("success"):
                urls = result.get("result", [])
                if urls:
                    print(f"✅ 上传成功: {urls[0]}")
                    return urls[0]
            
            print(f"❌ 上传失败: {result}")
            return ""
        except httpx.HTTPError as e:
            print(f"❌ 上传请求失败: {e}")
            return ""


async def upload_clipboard(picbed: str = None, config_name: str = None) -> str:
    """上传剪贴板中的图片
    
    返回:
        上传成功后的图片 URL
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            url = _build_url("upload")
            
            # 添加可选参数
            params = []
            if picbed:
                params.append(f"picbed={picbed}")
            if config_name:
                params.append(f"configName={config_name}")
            if params:
                separator = "&" if PICLIST_KEY else "?"
                url += separator + "&".join(params)
            
            response = await client.post(
                url,
                json={},
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            
            if result.get("success"):
                urls = result.get("result", [])
                if urls:
                    print(f"✅ 剪贴板图片上传成功: {urls[0]}")
                    return urls[0]
            
            print(f"❌ 上传失败: {result}")
            return ""
        except httpx.HTTPError as e:
            print(f"❌ 上传请求失败: {e}")
            return ""


async def delete_images(full_results: list[dict]) -> bool:
    """删除已上传的图片
    
    参数:
        full_results: fullResult 对象数组（从上传结果获取）
    
    返回:
        是否删除成功
    """
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                _build_url("delete"),
                json={"list": full_results},
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            
            if result.get("success"):
                print("✅ 删除成功")
                return True
            else:
                print(f"❌ 删除失败: {result}")
                return False
        except httpx.HTTPError as e:
            print(f"❌ 删除请求失败: {e}")
            return False

