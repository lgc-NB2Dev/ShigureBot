import datetime

from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Bot, MessageSegment
from nonebot_plugin_apscheduler import scheduler


def format_timedelta(t: datetime.timedelta):
    mm, ss = divmod(t.seconds, 60)
    hh, mm = divmod(mm, 60)
    s = "%d 时 %02d 分 %02d 秒" % (hh, mm, ss)
    if t.days:
        s = ("%d 天 " % t.days) + s
    if t.microseconds:
        s += " %.3f 毫秒" % (t.microseconds / 1000)
    return s


@scheduler.scheduled_job("cron", hour="*")
async def _():
    gaokao_t = datetime.datetime(2023, 6, 7)
    now = datetime.datetime.now()
    interval = gaokao_t - now
    bot: Bot = get_bot()
    await bot.send_group_msg(
        group_id=775075182,
        message=MessageSegment.at(80117801)
        + (
            f"\n"
            f"现在距离 2023 年高考还有\n"
            f"{interval.days}\n"
            f"Good good study, day day up!!"
        ),
    )
