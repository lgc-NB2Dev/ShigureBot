from nonebot import on_command
from nonebot.matcher import Matcher

from .data_source import get_soup


@on_command('毒鸡汤').handle()
async def _(matcher: Matcher):
    await matcher.send(get_soup())


__version__ = '0.1.0'
