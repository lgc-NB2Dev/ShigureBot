import random
import string

from nonebot import on_command, on_request
from nonebot.adapters.onebot.v11 import (Bot, FriendRequestEvent, GroupRequestEvent, Message, PRIVATE_FRIEND)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RawCommand
from nonebot.permission import SUPERUSER

from .config import config

agree_sample = ('-=-=-=-=-=-=-=-\n'
                '同意请求：#allow {0}{1}\n'
                '拒绝请求：#refuse {0}')
tmp = {}


def get_random_str(length: int = 6):
    return ''.join(random.sample(string.ascii_letters + string.digits, length))


@on_request().handle()
async def _(bot: Bot, event: FriendRequestEvent):
    if str(event.user_id) in bot.config.superusers and config.auto_allow_superusers:
        await bot.set_friend_add_request(flag=event.flag, approve=True)
        await bot.send_private_msg(user_id=event.user_id, message='已同意您的好友请求')
    elif config.forward_friend_req:
        rdm = get_random_str()
        tmp[rdm] = {'type': 'friend', 'flag': event.flag}
        for su in bot.config.superusers:
            await bot.send_private_msg(user_id=int(su),
                                       message=f'用户{event.user_id}请求加我为好友\n'
                                               f'验证信息：{event.comment}\n' +
                                               agree_sample.format(rdm, ' [备注]'))


def group_invite_rule(e: GroupRequestEvent):
    return e.sub_type == 'invite'


@on_request(rule=group_invite_rule).handle()
async def _(bot: Bot, event: GroupRequestEvent):
    if str(event.user_id) in bot.config.superusers and config.auto_allow_superusers:
        await bot.set_group_add_request(flag=event.flag, sub_type='invite', approve=True)
        await bot.send_private_msg(user_id=event.user_id, message='已同意您的邀请进群请求')
    elif config.forward_group_invite:
        rdm = get_random_str()
        tmp[rdm] = {'type': 'group', 'flag': event.flag}
        for su in bot.config.superusers:
            await bot.send_private_msg(user_id=int(su),
                                       message=f'用户{event.user_id}邀请我进群{event.group_id}\n' +
                                               agree_sample.format(rdm, ''))


@on_command(('#allow', '#refuse'), permission=SUPERUSER, rule=PRIVATE_FRIEND).handle()
async def _(bot: Bot, matcher: Matcher, cmd: str = RawCommand(), args: Message = CommandArg()):
    rdm, ex = args.extract_plain_text().split(' ', 1)
    req = tmp.get(rdm.strip())
    if req:
        approve = True if cmd == '#allow' else False
        approve_str = '同意' if approve else '拒绝'
        match req['type']:
            case 'friend':
                ex = ex.strip()
                await bot.set_friend_add_request(flag=req['flag'], approve=approve, remark=ex)
                await matcher.send(f'已{approve_str}该好友请求' + f'，备注已设为{ex}' if ex and approve else '')
            case 'group':
                await bot.set_group_add_request(flag=req['flag'], sub_type='invite', approve=approve)
                await matcher.send(f'已{approve_str}该邀请进群请求')
    else:
        await matcher.send('未找到该请求')


__version__ = '1.0.0'
