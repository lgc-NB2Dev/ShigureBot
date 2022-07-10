import asyncio
import os.path

import aiofiles
from nonebot import logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    MessageEvent,
    MessageSegment,
)
from nonebot_plugin_htmlrender import md_to_pic

from .config import config as conf
from .datatypes import BlackBEReturnDataInfo, ForwardMsg
from .get_data import *


def parse_lvl(lvl: int):
    if lvl == 1:
        msg = "有作弊行为，但未对其他玩家造成实质上损害"
    elif lvl == 2:
        msg = "有作弊行为，且对玩家造成一定的损害"
    elif lvl == 3:
        msg = "严重破坏服务器，对玩家和服务器造成较大的损害"
    else:
        msg = "未知"
    return f"等级{lvl}（{msg}）"


async def get_repo_name(_uuid):
    if _uuid == "1":
        return "公有库（1）"
    else:
        n = await get_repo_detail(_uuid, conf.token)
        return f'{n.name if n else "未知"}（{_uuid}）'


async def open_file_b(f_name):
    async with aiofiles.open(f_name, "rb") as f:
        return await f.read()


async def parse_info_md(info: BlackBEReturnDataInfo, uuid=""):
    black_id = info.black_id if info.black_id else uuid
    repo_name = await get_repo_name(black_id)

    im = list()
    im.append(f"- 玩家ID：{info.name}")
    im.append(f"- 危险等级：{parse_lvl(info.level)}")
    im.append(f"- 记录原因：{info.info}")
    if info.server:
        im.append(f"- 违规服务器：{info.server}")
    im.append(f"- XUID：{info.xuid}")
    im.append(f"- 玩家QQ：{info.qq}")
    if info.phone:
        im.append(f"- 玩家电话：+{info.area_code} {info.phone}")
    im.append(f"- 库来源：{repo_name}")
    if info.time:
        im.append(f"- 记录时间：{info.time}")
    im.append(f"- 记录UUID：{info.uuid}")
    im.extend(await get_img_msgs(info.photos, True))
    return "\n".join(im)


async def parse_info_group_forward(info: BlackBEReturnDataInfo, uuid=""):
    black_id = info.black_id if info.black_id else uuid
    repo_name = await get_repo_name(black_id)

    im = ForwardMsg()
    im.append(f"玩家ID：{info.name}")
    im.append(f"危险等级：{parse_lvl(info.level)}")
    im.append(f"记录原因：{info.info}")
    if info.server:
        im.append(f"违规服务器：{info.server}")
    im.append(f"XUID：{info.xuid}")
    im.append(f"玩家QQ：{info.qq}")
    if info.phone:
        im.append(f"玩家电话：+{info.area_code} {info.phone}")
    im.append(f"库来源：{repo_name}")
    if info.time:
        im.append(f"记录时间：{info.time}")
    im.append(f"记录UUID：{info.uuid}")
    if pics := (await get_img_msgs(info.photos)):
        im.append("以下是证据截图：")
        im.extend(pics)
    return im


async def get_img_msgs(info_photos, markdown=False):
    async def get_img_msg(photo):
        e = False
        pic_path = os.path.join(path, photo[photo.rfind("/") + 1 :])
        if not os.path.exists(pic_path):
            if not photo.startswith("http://") or photo.startswith("https://"):
                photo = "http://" + photo
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.get(photo) as raw:
                        p = await raw.read()
                async with aiofiles.open(pic_path, "wb") as f:
                    await f.write(p)
            except:
                e = True
                logger.exception("获取图片失败")

        if e:
            return f"获取图片失败（{photo}）"
        else:
            abs_path = os.path.abspath(pic_path)
            if markdown:
                return f"![]({abs_path})"
            return MessageSegment.image(await open_file_b(abs_path))

    path = "./shigure/blackbe_tmp"
    if not os.path.exists(path):
        os.makedirs(path)

    pics = []
    if info_photos:
        img_msg = await asyncio.gather(
            *[asyncio.create_task(get_img_msg(i)) for i in info_photos]
        )
        if markdown:
            pics.append("- 证据图片：  ")
        for pic in img_msg:
            pics.append(f"  {pic}  " if markdown else pic)
    return pics


async def send_info_msg(bot: Bot, ev: GroupMessageEvent | MessageEvent, **kwargs):
    group_forward = conf.use_group_forward_msg and isinstance(ev, GroupMessageEvent)

    async def get_msg(im: ForwardMsg):
        return im.get_msg((await bot.get_login_info())["nickname"], bot.self_id)

    async def parse_info(*args, **kws):
        return (
            (await get_msg(await parse_info_group_forward(*args, **kws)))
            if group_forward
            else (await parse_info_md(*args, **kws))
        )

    ret_simple = await get_simple_info(**kwargs)
    ret_repo = None
    if conf.token:
        ret_repo = await get_private_repo_info(conf.token, conf.ignore_repos, **kwargs)
    info = []
    tip_success = []
    tip_fail = []

    async def send_info_pic():
        msg = [
            (
                "<style>\n"
                "html{zoom:3}\n"  # 放大字体同时不影响图片清晰度
                "ul{padding-left:0px !important}\n"  # 将列表文本与页面主体左侧平齐
                "</style>"
            ),
            f"# 关于 {list(kwargs.values())[0]} 的查询结果：",
        ]
        if tip_success:
            msg.append(f'查询到{"，".join(tip_success)}')

        if tip_fail:
            msg.extend(tip_fail)

        if not tip_success and not tip_fail:
            msg.append("没有查询到任何记录")

        for ii in info:
            msg.append("----")
            msg.append(ii)

        img = await md_to_pic("\n\n".join(msg), width=1500)
        await bot.send(ev, MessageSegment.at(ev.user_id) + MessageSegment.image(img))

    async def send_info_forward():
        msg = [f"关于 {list(kwargs.values())[0]} 的查询结果："]
        if tip_success:
            msg.append(f'查询到{"，".join(tip_success)}')

        if tip_fail:
            msg.extend(tip_fail)

        if not tip_success and not tip_fail:
            msg.append("没有查询到任何记录捏～")
        else:
            msg.append("关于各条目详细信息请查看下方的转发消息～")

        await bot.send(ev, "\n".join(msg))
        for ii in info:
            await bot.send_group_forward_msg(group_id=ev.group_id, messages=ii)

    async def parse_ret():
        if isinstance(ret_simple, BlackBEReturn):
            if ret_simple.success:
                if ret_simple.data.exist:
                    tip_success.append(f" {len(ret_simple.data.info)} 条公有库记录")
                    for i in ret_simple.data.info:
                        t = await parse_info(i)
                        info.append(t)
            else:
                tip_fail.append(f"查询公有库记录失败：[{ret_simple.status}] {ret_simple.message}")
        else:
            tip_fail.append(f"查询公有库记录失败：{ret_simple!r}")

        if ret_repo:
            if isinstance(ret_repo, BlackBEReturn):
                if ret_repo.success:
                    count = 0
                    for i in ret_repo.data:
                        for n in i.info:
                            t = await parse_info(n, i.repo_uuid)
                            info.append(t)
                            count += 1
                    if count:
                        tip_success.append(
                            f" {len(ret_repo.data)} 个私有库的 {count} 条私有库记录"
                        )
                else:
                    tip_fail.append(f"查询私有库记录失败：[{ret_repo.status}] {ret_repo.message}")
            else:
                tip_fail.append(f"查询私有库记录失败：{ret_repo!r}")

    await parse_ret()

    if group_forward:
        try:
            await send_info_forward()
        except:
            logger.exception("发送合并转发消息失败")
            await bot.send(ev, "合并转发发送失败，尝试发送markdown图片")
            group_forward = False
            info.clear()
            tip_success.clear()
            tip_fail.clear()
            await parse_ret()
            await send_info_pic()
    else:
        await send_info_pic()
