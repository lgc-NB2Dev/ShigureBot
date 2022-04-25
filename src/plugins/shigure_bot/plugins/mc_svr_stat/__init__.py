from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .get_stat import motd as get_motd, motdpe as get_motdpe


@on_command('!motd', aliases={'!motdje'}, priority=2).handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    ret = await get_motd(str(args).strip())
    await matcher.finish(ret, at_sender=True)


@on_command('!motdfull').handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    ret = await get_motd(str(args).strip(), full=True)
    await matcher.finish(ret, at_sender=True)


@on_command('!motdpe', aliases={'!motdbe'}).handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    ret = await get_motdpe(str(args).strip())
    await matcher.finish(ret, at_sender=True)


__version__ = '0.1.0'
