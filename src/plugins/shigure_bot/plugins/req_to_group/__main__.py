import random
import string

from nonebot import logger, on_command, on_request
from nonebot.adapters.onebot.v11 import (ActionFailed, Bot, GroupMessageEvent, GroupRequestEvent,
                                         Message, MessageSegment)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

fwd_group_id = 1105946125
tmp = {}


def get_random_str(length: int = 6):
    return ''.join(random.sample(f'{string.ascii_letters}{string.digits}', length))


async def get_stranger_name(bot: Bot, qq):
    try:
        return (await bot.get_stranger_info(user_id=qq))['nickname']
    except ActionFailed:
        return '未知'


async def get_group_name(bot: Bot, group_id):
    try:
        return (await bot.get_group_info(group_id=group_id))['group_name']
    except ActionFailed:
        return '未知'


def group_invite_rule(event: GroupRequestEvent):
    return event.sub_type == 'invite'


@on_request(rule=group_invite_rule).handle()
async def _(bot: Bot, event: GroupRequestEvent):
    username = await get_stranger_name(bot, event.user_id)
    group_name = await get_group_name(bot, event.group_id)
    tmp[rdm := get_random_str()] = event
    await bot.send_group_msg(
        group_id=fwd_group_id,
        message=MessageSegment.at(event.user_id) +
                (f'\n'
                 f'{username}({event.user_id}) 邀请我进群 {group_name}({event.group_id})\n'
                 f'请您在本群发送 同意请求{rdm} 以自动同意该邀请进群请求')
    )


def group_rule(event: GroupMessageEvent):
    return event.group_id == fwd_group_id


@on_command('同意请求', rule=group_rule).handle()
async def _(bot: Bot, event: GroupMessageEvent, matcher: Matcher, args: Message = CommandArg()):
    rdm = args.extract_plain_text().strip()
    req: GroupRequestEvent = tmp.get(rdm)
    if req:
        if req.user_id == event.user_id:
            try:
                await req.approve(bot)
            except Exception as e:
                logger.opt(exception=e).exception('同意请求失败')
                await matcher.finish(f'同意请求失败，请重试\n{"；".join(e.args)}')
            else:
                await matcher.finish('同意请求成功！')

            del tmp[rdm]
        else:
            await matcher.finish('该请求不是你发起的！')

    await matcher.send('未找到请求')
