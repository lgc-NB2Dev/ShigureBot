from argparse import Namespace

from nonebot import on_shell_command
from nonebot.exception import ParserExit
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.rule import ArgumentParser

from .capture import get_msg
from .config import config

parser = ArgumentParser()
parser.add_argument("url", type=str, help="URL to capture")
parser.add_argument(
    "-d", "--delay", type=int, default=5, help="Delay after URL loaded before capture"
)
parser.add_argument("-wd", "--width", type=int, default=1280, help="Viewport width")
parser.add_argument("-hi", "--height", type=int, default=720, help="Viewport height")

handler = on_shell_command("网页截图", parser=parser)


@handler.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    url = args.url
    for i in config.ignore_sites:
        if url.find(i) != -1:
            await matcher.finish("服了你们了，搞事的都给爷爬", at_sender=True)

    delay = args.delay
    await matcher.send(f"\n请稍等，截图正在获取中～\n" f"页面加载完成{delay}秒后才会截图哦～", at_sender=True)
    msg = await get_msg(url, delay, args.width, args.height)
    await matcher.finish(msg, at_sender=True)


@handler.handle()
async def _(matcher: Matcher, e: ParserExit = ShellCommandArgs()):
    if e.status != 0:
        await matcher.finish(f"参数错误！请检查\n{e.message}", at_sender=True)
    await matcher.finish(f"\n{e.message}", at_sender=True)
