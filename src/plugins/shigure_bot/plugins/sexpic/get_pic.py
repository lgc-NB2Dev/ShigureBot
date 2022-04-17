import aiohttp
from nonebot.adapters.onebot.v11 import MessageSegment


async def get_pic(tag=''):
    params = {'proxy': 0, 'num': 1, 'tag': tag}

    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.lolicon.app/setu/v2', params=params) as response:
            ret = await response.json()
    ret = ret['data'][0]

    async with aiohttp.ClientSession() as session:
        async with session.get(ret['urls']['original'],
                               proxy="http://127.0.0.1:10809",
                               timeout=10,
                               headers={'referer': 'https://www.pixiv.net/'}) as response:
            pic = await response.read()

    detail = (f'\n奉上涩图一张~\n'
              f'PID：{ret["pid"]}\n'
              f'标题：{ret["title"]}\n'
              f'作者：{ret["author"]}\n'
              f'标签：{"；".join(ret["tags"])}')
    return MessageSegment.image(pic) + detail
