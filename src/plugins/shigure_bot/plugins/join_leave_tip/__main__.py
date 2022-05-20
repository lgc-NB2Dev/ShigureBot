from nonebot import on_notice
from nonebot.adapters.onebot.v11 import Bot, GroupDecreaseNoticeEvent, GroupIncreaseNoticeEvent, Message, MessageSegment
from nonebot.matcher import Matcher

from .config import config


async def parse_reply(reply: str, event: GroupIncreaseNoticeEvent | GroupDecreaseNoticeEvent, bot: Bot):
    return Message(reply.format(at=MessageSegment.at(event.user_id),
                                qq=event.user_id,
                                nick=(await bot.get_stranger_info(user_id=event.user_id))['nickname'],
                                admin=MessageSegment.at(event.operator_id)))


@on_notice(block=False).handle()
async def _(bot: Bot, matcher: Matcher, event: GroupIncreaseNoticeEvent):
    if not event.is_tome():
        await matcher.finish(await parse_reply(config.join_message, event, bot))


@on_notice(block=False).handle()
async def _(bot: Bot, matcher: Matcher, event: GroupDecreaseNoticeEvent):
    if not event.is_tome():
        match event.sub_type:
            case 'leave':
                await matcher.finish(await parse_reply(config.leave_message, event, bot))
            case 'kick':
                await matcher.finish(await parse_reply(config.kick_message, event, bot))


__version__ = '1.0.1'
