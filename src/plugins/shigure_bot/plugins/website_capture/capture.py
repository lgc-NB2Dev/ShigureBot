from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_htmlrender.browser import get_new_page
from playwright.async_api import Page, ViewportSize


async def get_capture(url, delay, width, height):
    async with get_new_page(
        viewport=ViewportSize(width=width, height=height)
    ) as page:  # type:Page
        await page.goto(url)
        await page.wait_for_timeout(delay * 1000)
        img = await page.screenshot(type="png", full_page=True)
    return img


async def get_msg(url: str, delay: int, width: int, height: int):
    if "http://" not in url and "https://" not in url:
        url = f"http://{url}"

    try:
        img = await get_capture(url, delay, width, height)
    except Exception as e:
        msg = f"出错了！请检查后台输出\n{e.args[0]}"
        logger.exception("获取网页截图出错")
    else:
        msg = MessageSegment.image(img)
    return msg
