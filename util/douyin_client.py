"""抖音创作者平台客户端 - 基于 Playwright
参考: https://github.com/dreammis/social-auto-upload
"""

import os
import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Page, BrowserContext

# 抖音创作者平台地址
DOUYIN_CREATOR_URL = "https://creator.douyin.com"
DOUYIN_UPLOAD_URL = "https://creator.douyin.com/creator-micro/content/upload"

# Cookie 存储路径
COOKIE_FILE = os.getenv("DOUYIN_COOKIE_FILE", "douyin_cookies.json")


async def save_cookies(context: BrowserContext):
    """保存 cookies 到文件"""
    cookies = await context.cookies()
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        json.dump(cookies, f, ensure_ascii=False, indent=2)
    print(f"✅ Cookies 已保存到 {COOKIE_FILE}")


async def load_cookies(context: BrowserContext) -> bool:
    """从文件加载 cookies"""
    if not os.path.exists(COOKIE_FILE):
        return False
    
    try:
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        print(f"✅ 已加载 Cookies")
        return True
    except Exception as e:
        print(f"❌ 加载 Cookies 失败: {e}")
        return False


async def check_login(page: Page) -> bool:
    """检查是否已登录"""
    try:
        await page.goto(DOUYIN_CREATOR_URL)
        await page.wait_for_load_state("networkidle", timeout=10000)
        
        # 检查是否有登录按钮（未登录状态）
        login_btn = await page.query_selector('div[class*="login"]')
        if login_btn:
            return False
        
        # 检查是否有用户头像（已登录状态）
        avatar = await page.query_selector('img[class*="avatar"]')
        if avatar:
            return True
        
        # 检查 URL 是否跳转到登录页
        if "login" in page.url:
            return False
        
        return True
    except Exception as e:
        print(f"检查登录状态失败: {e}")
        return False


async def login_with_qrcode(page: Page, context: BrowserContext) -> bool:
    """使用二维码登录抖音"""
    print("🔐 正在打开抖音登录页面...")
    
    await page.goto("https://creator.douyin.com/creator-micro/home")
    await page.wait_for_load_state("networkidle")
    
    print("📱 请使用抖音 APP 扫描二维码登录")
    print("⏳ 等待登录完成...")
    
    # 等待用户扫码登录（最多等待 120 秒）
    try:
        # 等待页面跳转到首页（登录成功后会跳转）
        await page.wait_for_url("**/creator-micro/home**", timeout=120000)
        await asyncio.sleep(2)
        
        # 检查 URL 是否还在登录页
        if "login" not in page.url:
            print("✅ 登录成功!")
            await save_cookies(context)
            return True
        else:
            print("❌ 登录失败")
            return False
    except Exception as e:
        print(f"❌ 登录超时或失败: {e}")
        return False


async def upload_video(
    page: Page,
    video_path: str,
    title: str,
    tags: list[str] = None,
    publish_time: str = None  # 格式: "2024-01-01 12:00"
) -> bool:
    """上传视频到抖音
    
    参数:
        page: Playwright 页面对象
        video_path: 视频文件绝对路径
        title: 视频标题
        tags: 标签列表（可选）
        publish_time: 定时发布时间（可选）
    
    返回:
        是否上传成功
    """
    print(f"📤 正在上传视频: {title}")
    
    try:
        # 打开上传页面
        await page.goto(DOUYIN_UPLOAD_URL)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(2)
        
        # 上传视频文件
        upload_input = await page.wait_for_selector('input[type="file"]', timeout=10000)
        await upload_input.set_input_files(video_path)
        
        print("⏳ 正在上传视频文件...")
        
        # 等待上传完成（检测进度条消失或完成提示）
        await page.wait_for_selector('div[class*="progress"]', state="hidden", timeout=300000)
        print("✅ 视频上传完成")
        
        await asyncio.sleep(2)
        
        # 填写标题
        title_input = await page.wait_for_selector('input[class*="title"]', timeout=5000)
        if title_input:
            await title_input.clear()
            await title_input.fill(title)
        
        # 添加标签
        if tags:
            for tag in tags:
                # 在描述区域输入标签
                desc_area = await page.query_selector('div[class*="desc"]')
                if desc_area:
                    await desc_area.type(f" #{tag}")
        
        await asyncio.sleep(1)
        
        # 点击发布按钮
        publish_btn = await page.wait_for_selector('button:has-text("发布")', timeout=5000)
        if publish_btn:
            await publish_btn.click()
            print("🚀 正在发布...")
            
            # 等待发布成功
            await asyncio.sleep(5)
            print("✅ 发布成功!")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ 上传失败: {e}")
        return False


async def upload_images(
    page: Page,
    image_paths: list[str],
    title: str,
    content: str = "",
    tags: list[str] = None
) -> bool:
    """上传图文到抖音
    
    参数:
        page: Playwright 页面对象
        image_paths: 图片文件绝对路径列表
        title: 标题
        content: 文案内容
        tags: 标签列表
    
    返回:
        是否上传成功
    """
    print(f"📤 正在上传图文: {title}")
    
    try:
        # 打开上传页面
        await page.goto(DOUYIN_UPLOAD_URL)
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)
        
        # 切换到图文模式
        print("🔄 切换到图文发布模式...")
        
        # 使用精确的选择器：class 包含 tab-item 且文本为 "发布图文"
        try:
            image_tab = await page.wait_for_selector('div[class*="tab-item"]:text-is("发布图文")', timeout=5000)
            await image_tab.click()
            print("✅ 已切换到图文模式")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"⚠️ 切换图文模式失败: {e}")
        
        # 批量上传图片
        print(f"⏳ 正在上传 {len(image_paths)} 张图片...")
        print(f"  📷 图片列表: {[os.path.basename(p) for p in image_paths]}")
        
        # 等待文件上传 input 出现
        upload_input = await page.wait_for_selector('input[type="file"][accept*="image"]', timeout=10000)
        if not upload_input:
            upload_input = await page.wait_for_selector('input[type="file"]', timeout=5000)
        
        # 一次性上传所有图片
        await upload_input.set_input_files(image_paths)
        
        # 等待所有图片上传完成
        await asyncio.sleep(3 + len(image_paths))  # 每张图片多等1秒
        
        print("✅ 图片上传完成")
        await asyncio.sleep(2)
        
        # 填写标题
        title_input = await page.query_selector('input[placeholder*="标题"]')
        if title_input:
            await title_input.fill(title)
        
        # 填写内容
        if content:
            content_area = await page.query_selector('textarea, div[contenteditable="true"]')
            if content_area:
                # 组合内容和标签
                full_content = content
                if tags:
                    tag_text = " ".join([f"#{tag}" for tag in tags])
                    full_content = f"{content}\n\n{tag_text}"
                
                await content_area.fill(full_content)
        
        await asyncio.sleep(1)
        
        print("\n✅ 内容已填写完成！")
        print("📝 请在浏览器中检查内容，手动点击发布按钮")
        print("🔒 关闭浏览器后程序将继续...\n")
        
        return True  # 填写成功
        
    except Exception as e:
        print(f"❌ 上传失败: {e}")
        return False


class DouyinClient:
    """抖音客户端封装"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    async def start(self):
        """启动浏览器"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=["--start-maximized"]  # 最大化窗口
        )
        self.context = await self.browser.new_context(
            no_viewport=True,  # 禁用固定 viewport，使用实际窗口大小
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = await self.context.new_page()
        
        # 尝试加载 cookies
        await load_cookies(self.context)
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def check_login(self) -> bool:
        """检查登录状态"""
        return await check_login(self.page)
    
    async def login(self) -> bool:
        """登录（显示二维码）"""
        return await login_with_qrcode(self.page, self.context)
    
    async def upload_video(self, video_path: str, title: str, tags: list[str] = None) -> bool:
        """上传视频"""
        return await upload_video(self.page, video_path, title, tags)
    
    async def upload_images(self, image_paths: list[str], title: str, content: str = "", tags: list[str] = None) -> bool:
        """上传图文"""
        return await upload_images(self.page, image_paths, title, content, tags)
    
    async def wait_for_close(self):
        """等待用户关闭浏览器"""
        if self.page:
            try:
                # 等待页面关闭
                await self.page.wait_for_event("close", timeout=0)
            except:
                pass
        
        # 清理资源
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except:
            pass
        
        print("🔒 浏览器已关闭")

