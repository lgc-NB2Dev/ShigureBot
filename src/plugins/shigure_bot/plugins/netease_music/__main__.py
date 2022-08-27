from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.params import Arg, ArgPlainText
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from .data_source import get_track_audio, login, search

pick_matcher = on_command("点歌", aliases={"网易云点歌", "网易点歌", "wyy", "netease", "ncm"})


def format_song_name(song):
    alia = f'（{"、".join(song["alia"])}）' if song["alia"] else ""
    return f'{song["name"]}{alia}'


def format_song_ars(song):
    return "、".join([x["name"] for x in song["ar"]])


@pick_matcher.handle()
async def _(state: T_State, args: Message = CommandArg()):
    if args.extract_plain_text().strip():
        state["song"] = args


@pick_matcher.got("song", "请发送你要点播的歌曲名称")
async def _(m: Matcher, state: T_State, name: str = ArgPlainText("song")):
    name = name.strip()
    if not name:
        await m.reject("此消息不包含文本，请重新发送你要点播的歌曲名称")

    try:
        ret = await search(name)
    except:
        logger.exception("网易云搜索失败")
        return await m.finish("搜索歌曲失败，请检查后台输出")

    if ret["code"] != 200:
        return await m.finish(f'未知错误({ret["code"]})')

    ret = ret["result"]
    if not ret.get("songs"):
        return await m.finish("未搜索到歌曲")

    state["ret"] = ret

    tmp = []
    for i, song in enumerate(ret["songs"]):
        tmp.append(f"{i + 1}. {format_song_name(song)} - {format_song_ars(song)}")

    song_li = "\n".join(tmp)
    await m.send(f"【{name}】的搜索结果：\n\n{song_li}\n\n" f"Tip：直接发送歌曲序号即可选择，发送0取消")


@pick_matcher.got("index")
async def _(m: Matcher, ret: dict = Arg("ret"), index: str = ArgPlainText("index")):
    index = index.strip()
    if not index.isdigit():
        await m.reject("选项只能为整数，请重新选择")

    index = int(index)
    if index == 0:
        return await m.finish("已取消选择")

    list_len = len(ret["songs"])
    if not 1 <= index <= list_len:
        await m.reject(f"选项只能为1~{list_len}，请重选")

    song = ret["songs"][index - 1]
    song_id = song["id"]
    try:
        ret_down = (
            await get_track_audio([song_id], bit_rate=song["privilege"]["playMaxbr"])
        )["data"]
    except:
        logger.exception("获取歌曲播放链接失败")
        return await m.finish("获取歌曲播放链接失败，请重试")

    if (not ret_down) or (not ret_down[0].get("url")):
        return await m.finish("未找到歌曲/歌曲没有下载链接")
    ret_down = ret_down[0]
    audio_url = ret_down["url"]

    title = format_song_name(song)
    ars = format_song_ars(song)
    await m.send(
        f"为您送上 {ars} 的歌曲 {title} ~\n"
        f'该歌曲音质为 {ret_down["level"]}，\n'
        f'歌曲文件大小为 {round(ret_down["size"] / 1024 / 1024, 2)} MB，\n'
        f"请注意流量消耗"
    )
    await m.send(
        MessageSegment.music_custom(
            audio_url, audio_url, title, ars, song["al"]["picUrl"]
        )
    )


@on_command("网易云重登", permission=SUPERUSER).handle()
async def _(m: Matcher):
    ret = await login()
    if isinstance(ret, Exception):
        return await m.finish(f"登录失败\n{ret!r}")
    await m.finish(f"登录成功")
