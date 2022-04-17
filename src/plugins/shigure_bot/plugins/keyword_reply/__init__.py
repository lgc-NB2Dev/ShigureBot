from nonebot import on_message
from nonebot.adapters.onebot.v11 import Event
from nonebot.matcher import Matcher

from .get_reply import get_reply


@on_message(priority=99).handle()
async def _(event: Event, matcher: Matcher):
    msg = await get_reply(str(event.get_message()), event.is_tome())
    if msg:
        await matcher.finish(msg)


__version__ = '0.1.0'
