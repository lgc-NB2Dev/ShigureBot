import aiohttp
from nonebot import on_command
from nonebot.adapters.onebot.v11.message import Message, MessageSegment
from nonebot.adapters.onebot.v11.utils import unescape
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER


@on_command("$访问", permission=SUPERUSER).handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    url = str(args).strip()
    if not url:
        await matcher.finish("请输入要访问的URL", at_sender=True)
        return
    if not url.startswith(("http://", "https://")):
        url = f"http://{unescape(url)}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                ret = await response.text()
    except Exception as e:
        await matcher.finish(f"URL访问失败：\n{e!r}", at_sender=True)
    else:
        await matcher.finish(f"URL返回内容：\n{ret}", at_sender=True)


@on_command("$img", permission=SUPERUSER).handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    url = str(args).strip()
    if not url:
        await matcher.finish("请输入要访问的URL", at_sender=True)
        return
    if not url.startswith(("http://", "https://")):
        url = f"http://{unescape(url)}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                ret = await response.read()
    except Exception as e:
        await matcher.finish(f"URL访问失败：\n{e!r}", at_sender=True)
    else:
        await matcher.finish(MessageSegment.image(ret), at_sender=True)
