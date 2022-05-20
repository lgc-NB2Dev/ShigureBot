from random import shuffle

import jieba
from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg


@on_command('打乱').handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    cut = list(jieba.cut(args.extract_plain_text()))
    shuffled = cut.copy()
    shuffle(shuffled)
    await matcher.send(f'原句：{"/".join(cut)}\n'
                       f'打乱：{"".join(shuffled)}')


logger.info('初始化结巴分词')
jieba.initialize()
# jieba.enable_paddle()  # py3.10无法使用，需求py3.7

__version__ = '0.1.0'
