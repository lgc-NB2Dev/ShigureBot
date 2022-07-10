import aiohttp
from nonebot.adapters.onebot.v11 import MessageSegment

from .config import config


async def get_pic(sender, tag=""):
    tag = tag.split(",")
    if len(tag) > 3:
        return "and规则的tag匹配数不能超过3个", True
    for i in tag:
        if len(i.split("|")) > 20:
            return "or规则的tag匹配数不能超过20个", True

    params = {
        "proxy": "i.pixiv.re" if config.proxy else "i.pximg.net",
        "num": 1,
        "tag": tag,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.lolicon.app/setu/v2", json=params
            ) as response:
                ret = await response.json()
    except:
        return "图片URL获取失败", True

    ret = ret["data"]
    if not ret:
        return "没有找到对应tag的图片", True
    ret = ret[0]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                ret["urls"]["original"],
                proxy=config.proxy,
                timeout=aiohttp.ClientTimeout(total=60),
                headers={"referer": "https://www.pixiv.net/"},
            ) as response:
                pic = await response.read()
    except:
        return "图片获取失败", True

    im = MessageSegment.image(pic)
    if config.send_details:
        im = (
            MessageSegment.at(sender)
            + im
            + (
                f"\n奉上涩图一张~\n"
                f'PID：{ret["pid"]}\n'
                f'标题：{ret["title"]}\n'
                f'作者：{ret["author"]}\n'
                f'标签：{"；".join(ret["tags"])}'
            )
        )
    return im, False
