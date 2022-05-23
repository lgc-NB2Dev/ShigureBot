from typing import Any

from nonebot import on_regex
from nonebot.adapters.onebot.v11 import Message
from nonebot.internal.params import ArgPlainText
from nonebot.matcher import Matcher
from nonebot.params import RegexGroup
from nonebot.typing import T_State

from .data_source import get_geng_msg

matcher = on_regex('([\s\S]*)是什么梗')


@matcher.handle()
async def _(state: T_State, args: tuple[Any, ...] = RegexGroup()):
    if arg := args[0].strip():
        state['phrase'] = Message() + arg


@matcher.got('phrase', '请问你想要了解一下什么梗呢？')
async def _(m: Matcher, phrase: str = ArgPlainText('phrase')):
    await m.finish('\n' + await get_geng_msg(phrase), at_sender=True)
