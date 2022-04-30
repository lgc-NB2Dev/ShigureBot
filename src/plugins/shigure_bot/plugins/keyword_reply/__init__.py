import random
import re

from nonebot import on_message
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment
from nonebot.matcher import Matcher

from .config import config as conf


async def parse_reply(reply: str, event: MessageEvent, bot: Bot):
    return Message(reply.format(at=MessageSegment.at(event.user_id),
                                qq=event.user_id,
                                nick=(await bot.get_stranger_info(user_id=event.user_id))['nickname']))


@on_message(priority=99).handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher):
    for reply in conf:
        if reply.to_me and (not event.is_tome()):
            continue  # not to me直接pass

        if reply.type == 'full':
            match = lambda m, kw: m == kw
        elif reply.type == 'fuzzy':
            match = lambda m, kw: m.find(kw) != -1
        elif reply.type == 'regex':
            match = lambda m, kw: re.fullmatch(kw, m) is not None
        else:
            match = lambda _, __: False

        for kwd in reply.keywords:
            if match(event.get_plaintext().lower().strip(), kwd.lower().strip()):
                await matcher.finish(await parse_reply(random.choice(reply.replies), event, bot))


__version__ = '0.1.3'
