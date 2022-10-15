from aiogram import Bot
from aiogram.types import InputMediaPhoto
from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageEvent
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from .config import config


@on_command('tg_sync', aliases={'tgsync', 'tg同步', '同步到tg'},
            permission=SUPERUSER).handle()
async def _(event: MessageEvent, matcher: Matcher, arg: Message = CommandArg()):
    if not (rep := event.reply):
        await matcher.finish('请回复你要同步到TG的消息')

    chats = {}
    if arg := arg.extract_plain_text().strip():
        for i in arg.split():
            if not (i in config.tg_chats.keys()):
                await matcher.finish(f'Chat {i} 在配置文件中不存在')
            chats[i] = config.tg_chats[i]
    else:
        chats = config.tg_chats

    if img := rep.message['image']:
        img = [x.data['url'] for x in img]

    from_ = f'{rep.sender.nickname}({rep.sender.user_id})'
    if isinstance(event, GroupMessageEvent):
        from_ = f'Group {event.group_id} -> {from_}'

    caption = (
        f'[ShigureBot - TGSync]\n'
        f'From: {from_}\n'
        f'{rep.message.extract_plain_text()}'
    )

    tg_bot = Bot(config.tg_bot_token, proxy=config.proxy)
    await matcher.send('开始同步到TG')
    for n, c in chats.items():
        try:
            if img:
                if len(img) > 1:
                    medias = [InputMediaPhoto(x) for x in img]
                    medias[-1].caption = caption
                    await tg_bot.send_media_group(c, medias)
                else:
                    await tg_bot.send_photo(c, img[0], caption)

            else:
                await tg_bot.send_message(c, caption)

        except Exception as e:
            logger.exception(f'同步到TG Chat {n}({c}) 失败')
            try:
                await matcher.send(f'同步到TG Chat {n}({c}) 失败，跳过\n{e!r}')
            except:
                pass
    await matcher.finish('同步到TG完毕，如没有失败提示则同步成功完成！')
