import time

from nonebot import logger, on_message
from nonebot.adapters.onebot.v11 import ActionFailed
from nonebot.adapters.onebot.v11.event import Event
from nonebot.exception import FinishedException
from nonebot.matcher import Matcher

from .config import config as conf
from .get_pic import *

temp = {'group': {}, 'private': {}}


@on_message(
    rule=lambda event: str(event.get_message()).startswith(tuple(conf.trigger_words))
).handle()
async def _(event: Event, matcher: Matcher):
    msg = str(event.get_message())
    if conf.only_private and event.message_type != 'private':
        return

    tmp_dict = temp.get(event.message_type)

    if tmp_dict is not None:
        chat_id = event.user_id if event.message_type == 'private' else event.group_id
        last_got = tmp_dict.get(chat_id)
        if last_got:
            time_passed = int(time.time() - last_got)
        else:
            time_passed = conf.delay

        if time_passed >= conf.delay:
            tmp_dict[chat_id] = time.time()
            await matcher.send('图片正在来的路上~\nPictures from Lolicon API')

            tag = ''
            for kw in conf.trigger_words:
                tag = msg.removeprefix(kw)
                if tag != msg:
                    break

            try:
                ret = await get_pic(tag.strip())
                await matcher.finish(ret, at_sender=True)
            except Exception as e:
                if isinstance(e, ActionFailed):
                    await matcher.finish('抱歉，消息被tx屏蔽…', at_sender=True)
                elif isinstance(e, IndexError):
                    await matcher.finish('没有找到图片', at_sender=True)
                elif isinstance(e, FinishedException):
                    pass
                else:
                    logger.exception('获取图片失败')
                    await matcher.finish('获取图片失败，请检查后台输出', at_sender=True)
                    tmp_dict[chat_id] = None
        else:
            await matcher.finish(f'图片冷却中……请等{120 - time_passed}秒再来吧', at_sender=True)


__version__ = '0.1.1'
