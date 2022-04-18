import re
from argparse import Namespace
from typing import Any

from nonebot import logger, on_regex, on_shell_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.exception import ParserExit
from nonebot.matcher import Matcher
from nonebot.params import RegexGroup, ShellCommandArgs
from nonebot.rule import ArgumentParser

from .datasource import get_cover

regexp = '^(https?:\/\/github\.com\/)?([^/]+)\/([^/]+)'

parser = ArgumentParser()
parser.add_argument('url', type=str, help='Github repo url')
parser.add_argument('--description', action='store_true', help='Show description')
parser.add_argument('--descriptionEditable', type=str, help='Custom description')
parser.add_argument('--font', type=str, help='Set font type', default='Inter',
                    choices=['Inter', 'Bitter', 'Raleway', 'Rokkitt', 'Source Code Pro', 'KoHo'])
parser.add_argument('--forks', action='store_true', help='Show fork num')
parser.add_argument('--issues', action='store_true', help='Show issue num')
parser.add_argument('--language', action='store_true', help='Show repo\'s main language')
parser.add_argument('--logo', type=str, help='Show Github logo / Custom logo (provide a pic link)')
parser.add_argument('--name', action='store_true', help='Show repo name')
parser.add_argument('--owner', action='store_true', help='Show repo owner')
parser.add_argument('--pattern', type=str, help='Set background pattern', default='Plus',
                    choices=['Signal', 'Charlie Brown', 'Formal Invitation', 'Plus', 'Circuit Board',
                             'Overlapping Hexagons', 'Brick Wall', 'Floating Cogs', 'Diagonal Stripes', 'Solid'])
parser.add_argument('--pulls', action='store_true', help='Show pr num')
parser.add_argument('--stargazers', action='store_true', help='Show star num')
parser.add_argument('--theme', type=str, help='Set pic theme', default='Light',
                    choices=['Light', 'Dark'])

handler = on_shell_command("socialify", parser=parser)


@handler.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    await matcher.finish(await get_im(re.match(regexp, args.url).groups(), **args.__dict__))


@handler.handle()
async def _(matcher: Matcher, e: ParserExit = ShellCommandArgs()):
    if not e.status == 0:
        await matcher.finish(f'参数错误！请检查\n{e.message}', at_sender=True)
    await matcher.finish(f'\n{e.message}', at_sender=True)


@on_regex(regexp, priority=99).handle()
async def _(matcher: Matcher, group: tuple[Any, ...] = RegexGroup()):
    logger.debug(str(group))
    await matcher.finish(await get_im(group))


async def get_im(group, **kwargs):
    try:
        ret = await get_cover(f'{group[1]}/{group[2]}', **kwargs)
    except (IndexError, TypeError) as e:
        logger.opt(exception=e).exception('获取Github仓库简介图失败')
        return '请输入正确格式的存储库链接'
    except Exception as e:
        logger.opt(exception=e).exception('获取Github仓库简介图失败')
        return f'获取Github仓库简介图失败：{e.args[0]}'
    else:
        return MessageSegment.image(ret)


__version__ = '0.1.0'
