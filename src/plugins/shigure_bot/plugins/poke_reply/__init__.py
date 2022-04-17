import random

import aiofiles
from nonebot import on_notice
from nonebot.adapters.onebot.v11 import Event, MessageSegment, PokeNotifyEvent
from nonebot.matcher import Matcher
from nonebot.rule import to_me

from .config import config as conf


async def read_file(file_name):
    async with aiofiles.open(file_name, 'rb') as f:
        ret = await f.read()
    return ret


@on_notice(rule=to_me()).handle()
async def _(event: Event, matcher: Matcher, _: PokeNotifyEvent):
    reply = random.choice(conf)
    msg = MessageSegment.image(await read_file(reply.content)) if reply.type == 'image' else reply.content
    await matcher.send(msg)
    if reply.action:
        await matcher.send(MessageSegment('poke', {'qq': event.user_id}))


__version__ = '0.2.0'
