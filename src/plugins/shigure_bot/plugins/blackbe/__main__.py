from nonebot import logger, on_command, on_message, require
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER

from .config import config as conf
from .detect import BlackBEDetect
from .get_msg import send_info_msg

detect = BlackBEDetect()
scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job("cron", minute="*/10")
async def _schedule_clear_noticed():
    detect.tmp_noticed.clear()


@scheduler.scheduled_job("cron", hour="*/12")
async def _schedule_clear_tmp():
    detect.tmp_black.clear()


def list_has_same_item(list1, list2):
    return any(i in list2 for i in list1)


@on_command("查云黑").handle()
async def _(
    bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()
):
    if at := args["at"]:
        await send_info_msg(bot, event, qq=at[0].data["qq"])
    elif msg := args.extract_plain_text().strip():
        await send_info_msg(bot, event, name=msg, qq=msg, xuid=msg)

    else:
        await matcher.finish("\n指令格式：查云黑<XboxID/QQ号/@某人/XUID>", at_sender=True)


@on_command("清除云黑缓存", permission=SUPERUSER).handle()
async def _(matcher: Matcher):
    detect.tmp_noticed.clear()
    detect.tmp_black.clear()
    await matcher.send("清除成功")


@on_message(block=False).handle()
async def _(event: GroupMessageEvent, matcher: Matcher):
    if not detect.has_noticed(event.group_id, event.user_id):
        ret = await detect.detect(event.user_id)
        if ret and ret.data:
            if ret.data.exist and not list_has_same_item(
                conf.ignore_repos, [x.uuid for x in ret.data.info]
            ):
                await matcher.send(
                    f"在BlackBE存在违规记录！\n" f"使用 查云黑{event.user_id} 查询详细信息",
                    at_sender=True,
                )
                detect.set_notice_stat(event.group_id, event.user_id, True)
        else:
            logger.exception(f"BlackBE检测失败！返回值不正常：{ret}")
