from typing import Any

from nonebot import on_command, on_regex
from nonebot.adapters.onebot.v11 import Message
from nonebot.internal.params import ArgPlainText
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RegexGroup
from nonebot.typing import T_State

from .data_source import get_geng_msg

matcher_command = on_command('梗百科')


@on_regex('([\s\S]+)是什么梗').handle()
async def _(matcher: Matcher, args: tuple[Any, ...] = RegexGroup()):
    arg = args[0].strip()
    await get_geng(matcher, arg)


@matcher_command.handle()
async def _(state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text().strip():
        state['phrase'] = args


@matcher_command.got('phrase', '请问你想要了解一下什么梗呢？')
async def _(m: Matcher, phrase: str = ArgPlainText('phrase')):
    if not (phrase := phrase.strip()):
        await m.reject('这条消息没有文本，无法查询……你到底想了解什么梗呢？请再发一遍')
    await get_geng(m, phrase)


async def get_geng(m: Matcher, phrase: str):
    await m.finish('\n' + await get_geng_msg(phrase), at_sender=True)
