from nonebot import on_command, on_message, require
from nonebot.adapters.onebot.v11 import Event, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .config import config as conf
from .datatypes import BlackBEReturn
from .get_data import get_simple_info
from .get_msg import get_info_msg
from .utils import list_has_same_item

base_ret = {
    "success" : True,
    "status"  : 2001,
    "message" : "用户不存在于黑名单中哦",
    "version" : "v3",
    "codename": "Moriya Suwako",
    "time"    : 0,
    "data"    : {"exist": False, "info": []}
}
temp = {'black': {}}
scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job("cron", minute="*/10")
async def delete_temp():
    global temp
    temp = {'black': {}}


@on_command('查云黑').handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    at = args['at']
    if at:
        ret = await get_info_msg(qq=at[0].data['qq'])
    else:
        msg = str(args).strip()
        if not msg:
            ret = '指令格式：查云黑<XboxID/QQ号/@某人/XUID>'
        else:
            ret = await get_info_msg(name=msg, qq=msg, xuid=msg)

    await matcher.finish('\n' + ret, at_sender=True)


@on_message(block=False).handle()
async def _(event: Event, matcher: Matcher):
    try:
        noticed = temp[f'{event.group_id}.{event.user_id}']
    except:
        noticed = False
    if not noticed:
        if temp['black'].get(event.user_id) is None:
            temp['black'][event.user_id] = BlackBEReturn(**base_ret)
            ret = await get_simple_info(token=conf.token, qq=event.user_id)
            temp['black'][event.user_id] = ret if isinstance(ret, BlackBEReturn) else None
        else:
            ret = temp['black'][event.user_id]

        if isinstance(ret, BlackBEReturn):
            if ret.data.exist:
                repos = [x.uuid for x in ret.data.info]
                if not list_has_same_item(conf.ignore_repos, repos):
                    await matcher.send(f'在BlackBE存在违规记录！\n'
                                       f'使用 查云黑{event.user_id} 查询详细信息',
                                       at_sender=True)
                    temp[f'{event.group_id}.{event.user_id}'] = True


__version__ = '1.1.2'
