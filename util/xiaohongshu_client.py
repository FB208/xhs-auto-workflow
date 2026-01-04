"""小红书创作者平台客户端 - 基于 Playwright + 反检测 + 人类行为模拟"""

import os
import json
import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext

from .stealth import (
    apply_stealth, human_delay, human_click, 
    remove_popups, find_visible_element, upload_files_visible
)

# 小红书创作者平台地址
XHS_CREATOR_URL = "https://creator.xiaohongshu.com"
XHS_UPLOAD_URL = "https://creator.xiaohongshu.com/publish/publish"

# Cookie 存储路径
COOKIE_FILE = os.getenv("XHS_COOKIE_FILE", "xiaohongshu_cookies.json")


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
        await page.goto(XHS_CREATOR_URL, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")
        await human_delay(2000, 4000)
        
        # 检查 URL 是否跳转到登录页
        if "login" in page.url:
            return False
        
        return True
    except Exception as e:
        print(f"检查登录状态失败: {e}")
        return False


async def login_with_qrcode(page: Page, context: BrowserContext) -> bool:
    """使用二维码登录小红书"""
    print("🔐 正在打开小红书登录页面...")
    
    await page.goto(XHS_CREATOR_URL, timeout=60000)
    await page.wait_for_load_state("domcontentloaded")
    
    print("📱 请使用小红书 APP 扫描二维码登录")
    print("⏳ 等待登录完成...")
    
    try:
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 120:
            await asyncio.sleep(2)
            if "login" not in page.url:
                print("✅ 登录成功!")
                await save_cookies(context)
                return True
        
        print("❌ 登录超时")
        return False
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return False


async def upload_images(
    page: Page,
    image_paths: list[str],
    title: str,
    content: str = "",
    tags: list[str] = None
) -> bool:
    """上传图文到小红书（带人类行为模拟）"""
    print(f"📤 正在上传图文到小红书...")
    
    try:
        # 打开发布页面
        await page.goto(XHS_UPLOAD_URL, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")
        await human_delay(3000, 5000)
        print("✅ 已进入发布页面")
        
        # 移除弹窗
        await remove_popups(page)
        
        # 切换到图文模式 - 只操作可见元素
        print("🔄 切换到图文模式...")
        
        image_tab = await find_visible_element(page, 'div.creator-tab')
        if image_tab:
            tabs = await page.locator('div.creator-tab').all()
            for tab in tabs:
                if await tab.is_visible():
                    box = await tab.bounding_box()
                    if box and box['x'] > 0:
                        text = await tab.inner_text()
                        if "上传图文" in text:
                            await human_click(tab)
                            await human_delay(1500, 2500)
                            print("✅ 已切换到图文模式")
                            break
        
        # 再次移除弹窗
        await remove_popups(page)
        
        # 上传图片
        print(f"⏳ 正在上传 {len(image_paths)} 张图片...")
        print(f"  📷 图片列表: {[os.path.basename(p) for p in image_paths]}")
        
        await upload_files_visible(page, 'input[type="file"]', image_paths)
        
        # 等待图片上传完成（带随机延迟）
        await human_delay(3000 + len(image_paths) * 2000, 5000 + len(image_paths) * 3000)
        print("✅ 图片上传完成")
        
        # 填写标题（只操作可见元素）
        if title:
            title_input = await find_visible_element(page, 'input[placeholder*="标题"]')
            if title_input:
                await human_click(title_input)
                await human_delay(300, 600)
                await title_input.fill(title)
                print(f"✅ 标题已填写: {title}")
            else:
                print("⚠️ 未找到可见的标题输入框")
        
        await human_delay(500, 1000)
        
        # 填写内容
        full_content = ""
        if content:
            full_content = content
        if tags:
            tag_text = " ".join([f"#{tag}" for tag in tags])
            full_content = f"{full_content}\n\n{tag_text}" if full_content else tag_text
        
        if full_content:
            content_area = await find_visible_element(page, 'div[contenteditable="true"]')
            if content_area:
                await human_click(content_area)
                await human_delay(300, 600)
                await content_area.fill(full_content)
                print("✅ 内容已填写")
            else:
                print("⚠️ 未找到可见的内容输入框")
        
        await human_delay(800, 1500)
        
        print("\n✅ 内容已填写完成！")
        print("📝 请在浏览器中检查内容，手动点击发布按钮")
        print("🔒 关闭浏览器后程序将继续...\n")
        
        return True
        
    except Exception as e:
        print(f"❌ 上传失败: {e}")
        return False


class XiaohongshuClient:
    """小红书客户端封装"""
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    async def start(self):
        """启动浏览器（带反检测）"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        self.context = await self.browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 应用反检测脚本
        await apply_stealth(self.context)
        
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
    
    async def upload_images(self, image_paths: list[str], title: str, content: str = "", tags: list[str] = None) -> bool:
        """上传图文"""
        return await upload_images(self.page, image_paths, title, content, tags)
    
    async def wait_for_close(self):
        """等待用户关闭浏览器"""
        if self.page:
            try:
                await self.page.wait_for_event("close", timeout=0)
            except:
                pass
        
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except:
            pass
        
        print("🔒 浏览器已关闭")
