from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from saucenao_api.params import DB

from .config import config
from .data_source import down_pic, saucenao_search


@on_command("搜图").handle()
async def _(
    bot: Bot, matcher: Matcher, event: MessageEvent, arg: Message = CommandArg()
):
    search_methods = {"saucenao": saucenao}

    method = m if (m := arg.extract_plain_text().strip()) else "saucenao"

    if method not in search_methods.keys():
        return await matcher.finish(f'搜图方式不存在！\n可用方式：{"/".join(search_methods.keys())}')

    pic: list[MessageSegment] = (
        event.reply.message["image"] if event.reply else event.message["image"]
    )
    if not pic:
        return await matcher.finish("请附带一张或者回复一张你要识别的图片")

    await matcher.send(f"正在使用 {method} 搜索，请稍等")
    msgs = await (search_methods[method])(pic[0].data["url"])

    if isinstance(msgs, list):
        if config.group_forward:
            self_nick = (await bot.get_login_info())["nickname"]
            msgs = [
                MessageSegment.node_custom(int(bot.self_id), self_nick, x) for x in msgs
            ]

            if isinstance(event, GroupMessageEvent):
                return await bot.send_group_forward_msg(
                    group_id=event.group_id, messages=msgs
                )
            elif isinstance(event, PrivateMessageEvent):
                return await bot.send_private_forward_msg(
                    user_id=event.user_id, messages=msgs
                )

        for m in msgs:
            await matcher.send(m)
    else:
        await matcher.send(msgs)


async def saucenao(pic) -> list[Message] | str:
    try:
        ret = await saucenao_search(url=pic, down_from_url=True)
    except Exception as e:
        logger.opt(exception=e).exception("saucenao搜索失败")
        return f"搜索失败！失败信息如下：\n{e!r}"

    if not ret:
        return "没有搜索到结果"

    ims = []
    for r in ret.results[: config.max_num]:
        urls = "\n".join(r.urls)
        source = next((k for k, v in DB.__dict__.items() if v == r.index_id), "未知")
        im = Message()
        try:
            im += MessageSegment.image(await down_pic(r.thumbnail, True))
        except:
            logger.exception("saucenao缩略图下载失败")
            im += f"缩略图下载失败\n{r.thumbnail}\n\n"
        im += (
            f"相似度：{r.similarity:.2f}%\n"
            f"来源：{source}\n"
            f"标题：{r.title}\n"
            f"作者：{r.author}\n"
            f"链接：{urls}"
        )
        ims.append(im)

    return ims
