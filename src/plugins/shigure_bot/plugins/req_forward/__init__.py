import random
import string

from nonebot import logger, on_command, on_request
from nonebot.adapters.onebot.v11 import (ActionFailed, Bot, FriendRequestEvent, GroupRequestEvent, Message,
                                         MessageEvent, PRIVATE_FRIEND)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RawCommand
from nonebot.permission import SUPERUSER

from .abc import ReqDict
from .config import config

agree_sample = ('-=-=-=-=-=-=-=-\n'
                '同意请求：#allow {0}{1}\n'
                '拒绝请求：#refuse {0}')
tmp = ReqDict()


def get_random_str(length: int = 6):
    return ''.join(random.sample(f'{string.ascii_letters}{string.digits}', length))


async def send_to_all_admins(bot, msg, excepts=None):
    if not excepts:
        excepts = []
    for su in bot.config.superusers:
        su = int(su)
        if su not in excepts:
            await bot.send_private_msg(user_id=su, message=msg)


async def get_stranger_name(bot, qq):
    return await bot.get_stranger_info(qq)['nickname']


async def get_group_name(bot, group_id):
    return await bot.get_group_info(group_id)['group_name']


@on_request().handle()
async def _(bot: Bot, event: FriendRequestEvent):
    username = await get_stranger_name(bot, event.user_id)
    sample = (f'用户 {username}({event.user_id}) 请求加我为好友\n'
              f'验证信息：{event.comment}')

    if str(event.user_id) in bot.config.superusers and config.auto_allow_superusers:
        await event.approve(bot)
        await bot.send_private_msg(user_id=event.user_id, message='已同意您的好友请求')

    elif config.auto_allow_anyone:
        await event.approve(bot)
        await send_to_all_admins(bot, sample.replace('\n', '，已自动同意\n', 1))

    elif config.forward_friend_req:
        if tmp.setitem(rdm := get_random_str(), event):
            await send_to_all_admins(bot,
                                     f'{sample}\n'
                                     f'{agree_sample.format(rdm, " [备注]")}')


def group_invite_rule(e: GroupRequestEvent):
    return e.sub_type == 'invite'


@on_request(rule=group_invite_rule).handle()
async def _(bot: Bot, event: GroupRequestEvent):
    username = await get_stranger_name(bot, event.user_id)
    group_name = await get_group_name(bot, event.group_id)
    sample = f'用户 {username}({event.user_id}) 邀请我进群 {group_name}({event.group_id})'

    if str(event.user_id) in bot.config.superusers and config.auto_allow_superusers:
        await event.approve(bot)
        await bot.send_private_msg(user_id=event.user_id, message='已同意您的邀请进群请求')

    elif config.auto_allow_anyone:
        await event.approve(bot)
        await send_to_all_admins(bot, f'{sample}，已自动同意')

    elif config.forward_group_invite:
        if tmp.setitem(rdm := get_random_str(), event):
            await send_to_all_admins(bot,
                                     f'{sample}\n'
                                     f'{agree_sample.format(rdm, "")}')


@on_command('#allow', aliases={'#refuse'}, permission=SUPERUSER | PRIVATE_FRIEND).handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher, cmd: str = RawCommand(), args: Message = CommandArg()):
    async def send_to_all_admins_except_sender(msg):
        await send_to_all_admins(bot, msg[event.sender])

    arg = args.extract_plain_text().split(' ', 1)
    rdm = arg[0].strip()
    ex = arg[1].strip() if len(arg) > 1 else None
    admin_name = await get_stranger_name(bot, event.sender)

    if req := tmp.get(rdm):
        approve_str = '同意' if (approve := (cmd == '#allow')) else '拒绝'
        tip_sample = f'管理员 {admin_name}({event.sender}) 已{approve_str}'

        try:
            if isinstance(req, FriendRequestEvent):
                await req.approve(bot)
                await matcher.send(f'已{approve_str}该好友请求'
                                   f'{(remark_tip := (f"，备注已设为{ex}" if ex and approve else ""))}')
                await send_to_all_admins_except_sender(f'{tip_sample}好友请求"{rdm}"{remark_tip}')

            elif isinstance(req, GroupRequestEvent):
                await req.approve(bot)
                await matcher.send(f'已{approve_str}该邀请进群请求')
                await send_to_all_admins_except_sender(f'{tip_sample}邀请进群请求"{rdm}"')

        except ActionFailed:
            logger.exception('请求处理出错')
            await matcher.finish('请求处理出错，请检查后台输出')
        tmp.pop(rdm)
    else:
        await matcher.finish('未找到该请求')


__version__ = '1.0.5'
