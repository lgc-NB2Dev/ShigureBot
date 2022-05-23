import asyncio

import aiohttp
from nonebot import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from .data_types import JikiResponse

SEARCH_URL = 'https://api.jikipedia.com/go/search_entities'


async def get_img_msg(url):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                return MessageSegment.image(await r.read())
    except:
        return MessageSegment.text(f'获取图片失败（{url}）')


async def get_geng_msg(name):
    async def get_geng():
        async with aiohttp.ClientSession() as s:
            async with s.post(
                    SEARCH_URL,
                    headers={'Client': 'web'},
                    json={'phrase': name, 'size': 20, 'page': 1}
            ) as r:
                rj = await r.json()
                # logger.debug(f'\n{json.dumps(rj, ensure_ascii=False, indent=2)}')
                return JikiResponse(**rj)

    try:
        ret = await get_geng()
    except:
        logger.exception('获取梗失败')
        return '抱歉，我还没Get到这个梗……（请求接口失败/返回值解析失败）'

    if not ret.data:
        return f'抱歉，我还没Get到这个梗……（{ret.message.title}：{ret.message.content}）'

    for da in ret.data:
        if da.definitions:
            for item in da.definitions:
                img = await asyncio.gather(*[
                    asyncio.create_task(get_img_msg(i)) for i in
                    [n.full.path for n in item.images]
                ]) if item.images else None
                text = item.plaintext.replace("\u200b", "").replace("\u200c", "")
                tags = ' '.join([f'#{x}' for x in [y.name for y in item.tags]]) if item.tags else '该词条还没有Tag哦～'

                im = Message()
                im += f'词条【{item.term.title}】：\n'
                im += f'{text}\n'
                if img:
                    im.extend(img)
                im += '\n'
                im += f'Tags：{tags}\n'
                im += f'原文：https://jikipedia.com/definition/{item.id}'
                return im

    return '抱歉，我还没Get到这个梗……（未找到词条）'
