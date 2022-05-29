import asyncio
import time

from nonebot import on_message
from nonebot.adapters.onebot.v11 import ActionFailed, Bot
from nonebot.adapters.onebot.v11.event import GroupMessageEvent, PrivateMessageEvent
from nonebot.matcher import Matcher

from .config import config as conf
from .get_pic import *

temp = {'group': {}, 'private': {}}


@on_message(
    rule=lambda event: str(event.get_message()).startswith(tuple(conf.trigger_words))
).handle()
async def _(bot: Bot, event: PrivateMessageEvent | GroupMessageEvent, matcher: Matcher):
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

            tag = ''
            for kw in conf.trigger_words:
                tag = msg.removeprefix(kw)
                if tag != msg:
                    break

            clear = True
            tag = tag.strip()
            if (not conf.can_filter_by_tag) and tag:
                await matcher.send('已关闭tag筛选功能，请不要使用tag筛选')
            else:
                await matcher.send('图片正在来的路上~\nPictures from Lolicon API')
                try:
                    ret, clear = await get_pic(event.sender.user_id, tag)
                    msg_id = (await matcher.send(ret))['message_id']
                except ActionFailed:
                    await matcher.finish('消息发送失败…', at_sender=True)

                if conf.withdraw_delay and (not clear):
                    # https://github.com/nonebot/adapter-onebot/commit/06956d210d70d4fc2471f39a97ec45f1995f5f0d
                    loop = asyncio.get_running_loop()
                    return loop.call_later(
                        conf.withdraw_delay,
                        lambda: loop.create_task(bot.delete_msg(message_id=msg_id)),
                    )

            if clear:
                tmp_dict[chat_id] = None
        else:
            await matcher.finish(f'图片冷却中……请等{conf.delay - time_passed}秒再来吧', at_sender=True)


__version__ = '0.1.5'
