import random
import string

from nonebot import logger, on_command, on_notice, on_request
from nonebot.adapters.onebot.v11 import (ActionFailed, Bot, FriendAddNoticeEvent, FriendRequestEvent,
                                         GroupDecreaseNoticeEvent, GroupIncreaseNoticeEvent, GroupRequestEvent,
                                         Message,MessageEvent, PRIVATE_FRIEND)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, RawCommand
from nonebot.permission import SUPERUSER

from .config import config

allow_cmd = 'allow'
refuse_cmd = 'refuse'
agree_sample = ('-=-=-=-=-=-=-=-\n'
                f'同意请求：{allow_cmd} {{0}}{{1}}\n'
                f'拒绝请求：{refuse_cmd} {{0}}')
tmp = dict()


def get_random_str(length: int = 6):
    return ''.join(random.sample(f'{string.ascii_letters}{string.digits}', length))


async def send_to_all_admins(bot: Bot, msg, excepts=None):
    if not excepts:
        excepts = []
    for su in bot.config.superusers:
        su = int(su)
        if su not in excepts:
            try:
                await bot.send_private_msg(user_id=su, message=msg)
            except:
                logger.exception('发送消息失败')
                pass


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


async def approve(ev, bot):
    try:
        await ev.approve(bot)
    except ActionFailed as e:
        return e
    return None


@on_request().handle()
async def _(bot: Bot, event: FriendRequestEvent):
    username = await get_stranger_name(bot, event.user_id)
    sample = (f'用户 {username}({event.user_id}) 请求加我为好友\n'
              f'验证信息：{event.comment}')

    if str(event.user_id) in bot.config.superusers and config.auto_allow_superusers:
        if not (e := await approve(event, bot)):
            await bot.send_private_msg(user_id=event.user_id, message='已同意您的好友请求')
        else:
            await bot.send_private_msg(user_id=event.user_id, message=f'自动同意请求失败：{e.info["wording"]}')

    elif config.auto_allow_anyone:
        if not (e := await approve(event, bot)):
            await send_to_all_admins(bot, sample.replace('\n', '，已自动同意\n', 1))
        else:
            await send_to_all_admins(bot, sample.replace('\n', f'，自动同意失败：{e.info["wording"]}\n', 1))

    elif config.forward_friend_req:
        tmp[rdm := get_random_str()] = event
        await send_to_all_admins(bot,
                                 f'{sample}\n'
                                 f'{agree_sample.format(rdm, " [备注]")}')


@on_request(rule=lambda event: event.sub_type == 'invite').handle()
async def _(bot: Bot, event: GroupRequestEvent):
    username = await get_stranger_name(bot, event.user_id)
    group_name = await get_group_name(bot, event.group_id)
    sample = f'用户 {username}({event.user_id}) 邀请我进群 {group_name}({event.group_id})'

    if str(event.user_id) in bot.config.superusers and config.auto_allow_superusers:
        if not (e := await approve(event, bot)):
            await bot.send_private_msg(user_id=event.user_id, message='已自动同意您的邀请进群请求')
        else:
            await bot.send_private_msg(user_id=event.user_id, message=f'自动同意请求失败：{e.info["wording"]}')

    elif config.auto_allow_anyone:
        if not (e := await approve(event, bot)):
            await send_to_all_admins(bot, f'{sample}，已自动同意')
        else:
            await send_to_all_admins(bot, f'{sample}，自动同意失败：{e.info["wording"]}')

    elif config.forward_group_invite:
        tmp[rdm := get_random_str()] = event
        await send_to_all_admins(bot,
                                 f'{sample}\n'
                                 f'{agree_sample.format(rdm, "")}')


@on_notice(block=False).handle()
async def _(bot: Bot, event: GroupIncreaseNoticeEvent):
    if event.is_tome() and config.send_addition_notice:
        await send_to_all_admins(bot, f'新添加群 {await get_group_name(bot, event.group_id)}({event.group_id})')


@on_notice(block=False).handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent):
    if event.is_tome() and config.send_leave_notice:
        action_name = '主动退出' if event.sub_type == 'leave' else '被踢出'
        await send_to_all_admins(bot, f'{action_name}群 {await get_group_name(bot, event.group_id)}({event.group_id})')


@on_notice(block=False).handle()
async def _(bot: Bot, event: FriendAddNoticeEvent):
    if config.send_addition_notice:
        await send_to_all_admins(bot, f'新添加好友 {await get_stranger_name(bot, event.user_id)}({event.user_id})')


@on_command(allow_cmd, aliases={refuse_cmd}, permission=SUPERUSER | PRIVATE_FRIEND).handle()
async def _(bot: Bot, event: MessageEvent, matcher: Matcher, cmd: str = RawCommand(), args: Message = CommandArg()):
    async def process(ev, act):
        if act:
            await ev.approve(bot)
        else:
            await ev.reject(bot)

    arg = args.extract_plain_text().split(' ', 1)
    rdm = arg[0].strip()
    ex = arg[1].strip() if len(arg) > 1 else None

    if req := tmp.get(rdm):
        approve_str = '同意' if (is_approve := (cmd == allow_cmd)) else '拒绝'
        tip_sample = f'管理员 {event.sender.nickname}({event.sender.user_id}) 已{approve_str}'

        try:
            await process(req, is_approve)
            req_name = '好友' if isinstance(req, FriendRequestEvent) else '邀请进群'
            await matcher.send(f'已{approve_str}该{req_name}请求'
                               f'{(remark_tip := (f"，备注已设为{ex}" if ex and is_approve else ""))}')
            await send_to_all_admins(bot,
                                     f'{tip_sample}{req_name}请求"{rdm}"{remark_tip}',
                                     [event.sender.user_id])

        except ActionFailed as e:
            logger.opt(exception=e).exception('请求处理出错')
            await matcher.finish(f'请求处理出错：{e.info["wording"]}')
        tmp.pop(rdm)
    else:
        await matcher.finish('未找到该请求')


__version__ = '1.1.1'
