"""抖音创作者平台客户端 - 基于 Playwright + 反检测 + 人类行为模拟"""

import os
import json
import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext

from .stealth import (
    apply_stealth, human_delay, human_click,
    remove_popups, find_visible_element, upload_files_visible
)
from .console import print_success, print_error, print_info, print_warning

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
    print_success(f"Cookies 已保存到 {COOKIE_FILE}")


async def load_cookies(context: BrowserContext) -> bool:
    """从文件加载 cookies"""
    if not os.path.exists(COOKIE_FILE):
        return False
    
    try:
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        await context.add_cookies(cookies)
        print_success("已加载 Cookies")
        return True
    except Exception as e:
        print_error(f"加载 Cookies 失败: {e}")
        return False


async def check_login(page: Page) -> bool:
    """检查是否已登录"""
    try:
        await page.goto(DOUYIN_CREATOR_URL)
        await page.wait_for_load_state("networkidle", timeout=15000)
        await human_delay(2000, 4000)
        
        # 优先检测页面是否有"验证码登录"文字，有则说明未登录
        try:
            login_text = page.locator('text=验证码登录')
            if await login_text.is_visible(timeout=2000):
                print_info("检测到'验证码登录'，需要登录")
                return False
        except:
            pass
        
        # 如果没有"验证码登录"，说明已登录
        print_success("已自动登录（未检测到登录页面）")
        return True
        
    except Exception as e:
        print_error(f"检查登录状态失败: {e}")
        return False


async def login_with_qrcode(page: Page, context: BrowserContext) -> bool:
    """使用二维码登录抖音"""
    print_info("正在打开抖音登录页面...")
    
    await page.goto("https://creator.douyin.com/creator-micro/home")
    await page.wait_for_load_state("networkidle")
    
    print_info("请使用抖音 APP 扫描二维码登录")
    print_info("等待登录完成...")
    
    try:
        await page.wait_for_url("**/creator-micro/home**", timeout=120000)
        await human_delay(1500, 3000)
        
        if "login" not in page.url:
            print_success("登录成功!")
            await save_cookies(context)
            return True
        else:
            print_error("登录失败")
            return False
    except Exception as e:
        print_error(f"登录超时或失败: {e}")
        return False


async def upload_images(
    page: Page,
    image_paths: list[str],
    title: str,
    content: str = "",
    tags: list[str] = None
) -> bool:
    """上传图文到抖音（带人类行为模拟）"""
    print_info(f"正在上传图文: {title}")
    
    try:
        await page.goto(DOUYIN_UPLOAD_URL)
        await page.wait_for_load_state("networkidle")
        await human_delay(2000, 4000)
        
        await remove_popups(page)
        
        print_info("切换到图文发布模式...")
        
        image_tab = await find_visible_element(page, 'div[class*="tab-item"]')
        if image_tab:
            tabs = await page.locator('div[class*="tab-item"]').all()
            for tab in tabs:
                if await tab.is_visible():
                    box = await tab.bounding_box()
                    if box and box['x'] > 0:
                        text = await tab.inner_text()
                        if "发布图文" in text:
                            await human_click(tab)
                            await human_delay(1500, 2500)
                            print_success("已切换到图文模式")
                            break
        
        await remove_popups(page)
        
        print_info(f"正在上传 {len(image_paths)} 张图片...")
        
        await upload_files_visible(page, 'input[type="file"][accept*="image"]', image_paths)
        
        await human_delay(3000 + len(image_paths) * 1500, 5000 + len(image_paths) * 2500)
        print_success("图片上传完成")
        
        title_input = await find_visible_element(page, 'input[placeholder*="标题"]')
        if title_input:
            await human_click(title_input)
            await human_delay(300, 600)
            await title_input.fill(title)
            print_success(f"标题已填写: {title}")
        
        await human_delay(500, 1000)
        
        if content:
            content_area = await find_visible_element(page, 'textarea, div[contenteditable="true"]')
            if content_area:
                full_content = content
                if tags:
                    tag_text = " ".join([f"#{tag}" for tag in tags])
                    full_content = f"{content}\n\n{tag_text}"
                
                await human_click(content_area)
                await human_delay(300, 600)
                await content_area.fill(full_content)
                print_success("内容已填写")
        
        await human_delay(800, 1500)
        
        print_success("内容已填写完成！")
        print_info("请在浏览器中检查内容，手动点击发布按钮")
        print_info("关闭浏览器后程序将继续...")
        
        return True
        
    except Exception as e:
        print_error(f"上传失败: {e}")
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
        
        await apply_stealth(self.context)
        
        self.page = await self.context.new_page()
        
        await load_cookies(self.context)
    
    async def close(self):
        """关闭浏览器"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def check_login(self) -> bool:
        return await check_login(self.page)
    
    async def login(self) -> bool:
        return await login_with_qrcode(self.page, self.context)
    
    async def wait_for_manual_login(self):
        """等待用户手动完成登录（不刷新页面）"""
        # 检查当前页面是否已经是登录页面，如果不是才导航
        current_url = self.page.url
        if "creator.douyin.com" not in current_url:
            await self.page.goto("https://creator.douyin.com/creator-micro/home")
            await self.page.wait_for_load_state("networkidle")
        
        print_info("请在浏览器中扫码登录抖音（需要输入短信验证码）")
        print_warning("⚠️ 登录完成后再按回车，不要提前按！")
        
        # 使用 asyncio 在后台等待用户输入
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: input("登录完成后按回车键继续..."))
        
        # 保存 cookies（不刷新页面）
        await save_cookies(self.context)
        print_success("已保存登录状态")
    
    async def upload_images(self, image_paths: list[str], title: str, content: str = "", tags: list[str] = None) -> bool:
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
        
        print_info("浏览器已关闭")
