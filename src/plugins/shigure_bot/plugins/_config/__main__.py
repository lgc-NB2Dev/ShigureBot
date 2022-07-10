from nonebot import on_regex
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER

from .config import *


@on_regex("^重载配置$", permission=SUPERUSER).handle()
async def _(matcher: Matcher):
    await matcher.send("请稍候")
    try:
        await reload()
    except:
        logger.exception("配置重载失败")
        await matcher.finish("操作失败，请检查后台输出")
    else:
        await matcher.finish("操作完毕")
