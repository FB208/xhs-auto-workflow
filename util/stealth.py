"""Playwright 反检测与人类行为模拟工具"""

import random
import asyncio
from playwright.async_api import Page, BrowserContext, Locator


# ========== 反检测脚本 ==========

STEALTH_JS = """
// 修改 navigator.webdriver
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// 修改 navigator.plugins
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });

// 修改 navigator.languages
Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });

// 移除 Chromium 自动化特征
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

// 伪造 chrome 对象
window.chrome = { runtime: {} };

// 修改权限查询
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => (
    parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
);
"""


async def apply_stealth(context: BrowserContext):
    """应用反检测脚本到浏览器上下文"""
    await context.add_init_script(STEALTH_JS)


# ========== 人类行为模拟 ==========

async def human_delay(min_ms: int = 500, max_ms: int = 1500):
    """模拟人类操作间隔（随机延迟）
    
    参数:
        min_ms: 最小延迟（毫秒）
        max_ms: 最大延迟（毫秒）
    """
    delay = random.randint(min_ms, max_ms) / 1000
    await asyncio.sleep(delay)


async def human_click(locator: Locator):
    """模拟人类点击（带随机偏移和延迟）"""
    await human_delay(300, 800)
    
    # 获取元素边界
    box = await locator.bounding_box()
    if box:
        # 在元素内随机位置点击（不是正中心）
        x_offset = random.randint(int(box['width'] * 0.2), int(box['width'] * 0.8))
        y_offset = random.randint(int(box['height'] * 0.2), int(box['height'] * 0.8))
        await locator.click(position={"x": x_offset, "y": y_offset})
    else:
        await locator.click()
    
    await human_delay(200, 500)


# ========== 弹窗处理 ==========

# 常见弹窗选择器
POPUP_SELECTORS = [
    '.pop-cover',           # 小红书弹窗
    '.modal-mask',          # 通用遮罩
    '.dialog-mask',         # 对话框遮罩
    '.overlay',             # 覆盖层
    '[class*="popup"]',     # 包含 popup 的类
    '[class*="modal"]',     # 包含 modal 的类
    '[class*="dialog"]',    # 包含 dialog 的类
    '.ant-modal-mask',      # Ant Design 遮罩
    '.ant-modal-wrap',      # Ant Design 弹窗
    '.weui-dialog__mask',   # WeUI 遮罩
]


async def remove_popups(page: Page):
    """移除可能遮挡操作的弹窗元素"""
    for selector in POPUP_SELECTORS:
        try:
            await page.evaluate(f"""
                document.querySelectorAll('{selector}').forEach(el => {{
                    if (el.style.display !== 'none' && el.offsetParent !== null) {{
                        console.log('Removing popup:', '{selector}');
                        el.remove();
                    }}
                }});
            """)
        except:
            pass
    await asyncio.sleep(0.3)


async def close_popups(page: Page):
    """尝试点击关闭按钮来关闭弹窗"""
    close_selectors = [
        '[class*="close"]',
        '[aria-label="关闭"]',
        '[aria-label="Close"]',
        'button:has-text("关闭")',
        'button:has-text("取消")',
        'button:has-text("我知道了")',
        'button:has-text("确定")',
        '.ant-modal-close',
    ]
    
    for selector in close_selectors:
        try:
            close_btn = page.locator(selector).first
            if await close_btn.is_visible():
                await close_btn.click()
                await human_delay(300, 600)
                return True
        except:
            pass
    
    return False


# ========== 可见元素操作 ==========

async def wait_for_visible(page: Page, selector: str, timeout: int = 10000) -> Locator:
    """等待元素可见并返回定位器
    
    参数:
        page: 页面对象
        selector: CSS 选择器
        timeout: 超时时间（毫秒）
    
    返回:
        可见的元素定位器
    
    异常:
        如果元素不可见则抛出异常
    """
    locator = page.locator(selector)
    await locator.first.wait_for(state="visible", timeout=timeout)
    return locator.first


async def find_visible_element(page: Page, selector: str) -> Locator | None:
    """查找第一个可见的元素
    
    参数:
        page: 页面对象
        selector: CSS 选择器
    
    返回:
        第一个可见的元素定位器，如果没有则返回 None
    """
    elements = await page.locator(selector).all()
    
    for el in elements:
        try:
            if await el.is_visible():
                box = await el.bounding_box()
                # 确保元素在可视区域内（排除 left: -9999px 等情况）
                if box and box['x'] > 0 and box['y'] > 0:
                    return el
        except:
            pass
    
    return None


async def upload_files_visible(page: Page, selector: str, files: list[str], timeout: int = 10000):
    """上传文件到可见的 input 元素
    
    注意: file input 通常是隐藏的，这里会先让它可见
    
    参数:
        page: 页面对象
        selector: input[type="file"] 的选择器
        files: 文件路径列表
        timeout: 超时时间（毫秒）
    """
    # 先移除可能的弹窗
    await remove_popups(page)
    
    # file input 通常是 display:none，需要通过 set_input_files 直接操作
    # 但我们先确保它存在
    locator = page.locator(selector).first
    await locator.wait_for(state="attached", timeout=timeout)
    
    await human_delay(500, 1000)
    await locator.set_input_files(files)
    await human_delay(1000, 2000)

