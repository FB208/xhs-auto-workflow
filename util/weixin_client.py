"""微信视频号创作者平台客户端 - 基于 Playwright + 反检测 + 人类行为模拟"""

import os
import json
import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext

from .stealth import (
    apply_stealth, human_delay, human_click,
    remove_popups, find_visible_element, upload_files_visible
)
from .console import print_success, print_error, print_info, print_warning

# 视频号创作者平台地址
WEIXIN_CREATOR_URL = "https://channels.weixin.qq.com"
WEIXIN_UPLOAD_URL = "https://channels.weixin.qq.com/platform/post/finderNewLifeCreate"

# Cookie 存储路径
COOKIE_FILE = os.getenv("WEIXIN_COOKIE_FILE", "weixin_cookies.json")


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
        await page.goto(WEIXIN_CREATOR_URL)
        await page.wait_for_load_state("networkidle", timeout=15000)
        await human_delay(2000, 4000)
        
        if "login" in page.url:
            return False
        
        qrcode = await page.query_selector('img[class*="qrcode"]')
        if qrcode:
            return False
        
        return True
    except Exception as e:
        print_error(f"检查登录状态失败: {e}")
        return False


async def login_with_qrcode(page: Page, context: BrowserContext) -> bool:
    """使用二维码登录视频号"""
    print_info("正在打开视频号登录页面...")
    
    await page.goto(WEIXIN_CREATOR_URL)
    await page.wait_for_load_state("networkidle")
    
    print_info("请使用微信扫描二维码登录")
    print_info("等待登录完成...")
    
    try:
        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < 120:
            await asyncio.sleep(2)
            if "login" not in page.url and "qrcode" not in page.url:
                user_info = await page.query_selector('[class*="user"], [class*="avatar"]')
                if user_info:
                    print_success("登录成功!")
                    await save_cookies(context)
                    return True
        
        print_error("登录超时")
        return False
    except Exception as e:
        print_error(f"登录失败: {e}")
        return False


async def upload_images(
    page: Page,
    image_paths: list[str],
    title: str,
    content: str = "",
    tags: list[str] = None
) -> bool:
    """上传图文到视频号（带人类行为模拟）"""
    print_info("正在上传图文到视频号...")
    
    try:
        await page.goto(WEIXIN_UPLOAD_URL, timeout=60000)
        await page.wait_for_load_state("domcontentloaded")
        await human_delay(3000, 5000)
        print_success("已进入图文发布页面")
        
        await remove_popups(page)
        
        print_info(f"正在上传 {len(image_paths)} 张图片...")
        
        await upload_files_visible(page, '.ant-upload-btn input[type="file"]', image_paths)
        
        await human_delay(3000 + len(image_paths) * 1500, 5000 + len(image_paths) * 2500)
        print_success("图片上传完成")
        
        if title:
            title_input = await find_visible_element(page, 'input[placeholder="填写标题, 22个字符内"]')
            if title_input:
                await human_click(title_input)
                await human_delay(300, 600)
                await title_input.fill(title)
                print_success(f"标题已填写: {title}")
            else:
                print_warning("未找到可见的标题输入框")
        
        await human_delay(500, 1000)
        
        full_desc = ""
        if content:
            full_desc = content
        if tags:
            tag_text = " ".join([f"#{tag}" for tag in tags])
            full_desc = f"{full_desc}\n\n{tag_text}" if full_desc else tag_text
        
        if full_desc:
            desc_area = await find_visible_element(page, 'div.input-editor[data-placeholder*="描述"]')
            if desc_area:
                await human_click(desc_area)
                await human_delay(300, 600)
                await desc_area.fill(full_desc)
                print_success("描述已填写")
            else:
                print_warning("未找到可见的描述输入框")
        
        await human_delay(800, 1500)
        
        print_success("内容已填写完成！")
        print_info("请在浏览器中检查内容，手动点击发布按钮")
        print_info("关闭浏览器后程序将继续...")
        
        return True
        
    except Exception as e:
        print_error(f"上传失败: {e}")
        return False


class WeixinClient:
    """视频号客户端封装"""
    
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
