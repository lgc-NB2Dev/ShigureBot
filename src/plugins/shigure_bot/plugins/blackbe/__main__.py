from nonebot import logger, on_command, on_message, require
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .config import config as conf
from .detect import BlackBEDetect
from .get_msg import send_info_msg

detect = BlackBEDetect()
scheduler = require("nonebot_plugin_apscheduler").scheduler


def list_has_same_item(list1, list2):
    for i in list1:
        if i in list2:
            return True
    return False


@scheduler.scheduled_job("cron", minute="*/10")
async def delete_temp():
    detect.clear_tmp()


@on_command("查云黑").handle()
async def _(
        bot: Bot, event: MessageEvent, matcher: Matcher, args: Message = CommandArg()
):
    if at := args["at"]:
        await send_info_msg(bot, event, qq=at[0].data["qq"])
    else:
        if not (msg := args.extract_plain_text().strip()):
            await matcher.finish(" \n指令格式：查云黑<XboxID/QQ号/@某人/XUID>", at_sender=True)
        else:
            await send_info_msg(bot, event, name=msg, qq=msg, xuid=msg)


@on_message(block=False).handle()
async def _(event: GroupMessageEvent, matcher: Matcher):
    if not detect.has_noticed(event.group_id, event.user_id):
        ret = await detect.detect(event.user_id)
        if ret and ret.data:
            if ret.data.exist:
                if not list_has_same_item(
                        conf.ignore_repos, [x.uuid for x in ret.data.info]
                ):
                    await matcher.send(
                        f"在BlackBE存在违规记录！\n" f"使用 查云黑{event.user_id} 查询详细信息", at_sender=True
                    )
                    detect.set_notice_stat(event.group_id, event.user_id, True)
        else:
            logger.exception(f'BlackBE检测失败！返回值不正常：{ret}')
