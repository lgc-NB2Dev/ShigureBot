import aiohttp
from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .config import config

hito_types = {
    '动画'  : 'a',
    '漫画'  : 'b',
    '游戏'  : 'c',
    '文学'  : 'd',
    '原创'  : 'e',
    '来自网络': 'f',
    '其他'  : 'g',
    '影视'  : 'h',
    '诗词'  : 'i',
    '网易云' : 'j',
    '哲学'  : 'k',
    '抖机灵' : 'l'
}


async def aiohttp_get(*args, **kwargs):
    async with aiohttp.ClientSession() as s:
        async with s.get(*args, **kwargs) as resp:
            return await resp.json()


@on_command('一言').handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    args = args.extract_plain_text().strip()
    params = ''
    if args:
        args = [x.strip() for x in args.split(' ')]
        params = []
        for i in args:
            hito_type = hito_types.get(i)
            if not hito_type:
                await matcher.finish(f'不支持的句子类型“{i}”，可用类型：{"/".join(hito_types.keys())}，多个类型用空格分隔')
            params.append(hito_type)
        params = f'?c={"&c=".join(params)}'

    try:
        ret = await aiohttp_get(f'https://v1.hitokoto.cn{params}')
    except:
        logger.exception('获取一言失败')
        await matcher.finish('获取句子失败，请检查后台输出')
    else:
        who = ret['from_who']
        await matcher.finish(f'『{ret["hitokoto"]}』\n'
                             f'—— {who if who else ""}「{ret["from"]}」' +
                             (f'\n(https://hitokoto.cn?uuid={ret["uuid"]})' if config.send_link else ''))
