import asyncio

from nonebot import logger
from pyncm import GetCurrentSession
from pyncm.apis import WeapiCryptoRequest
from pyncm.apis.cloudsearch import GetSearchResult, SONG
from pyncm.apis.login import LoginViaCellphone
from pyncm.apis.track import GetTrackAudio, GetTrackDetail

from .config import config
from .util import async_wrapper as wrapper

if config.fake_ip:
    GetCurrentSession().headers["X-Real-IP"] = config.fake_ip


async def login():
    if not config.login:
        return ValueError("配置文件中 netease_login 不为真")
    logger.info("开始登录网易云音乐")
    try:
        ret = await wrapper(
            LoginViaCellphone,
            phone=config.phone,
            password=config.pwd,
            ctcode=config.ct_code,
        )
        nick = ret["result"]["content"]["profile"]["nickname"]
    except Exception as e:
        logger.opt(exception=e).exception("登录失败，功能将会受到限制")
        return e
    logger.info(f"欢迎您，{nick}")


asyncio.run(login())


async def search(name, limit=config.list_limit, page=1, stype=SONG):
    offset = limit * (page - 1)
    res = await wrapper(GetSearchResult, name, stype=stype, limit=limit, offset=offset)
    logger.debug(f"GetSearchResult - {res}")
    return res


async def search_dj(name, limit=config.list_limit, page=1):
    offset = limit * (page - 1)

    @WeapiCryptoRequest  # type:ignore
    def get():
        return "/api/search/voice/get", {
            "keyword": name,
            "scene": "normal",
            "limit": limit or 30,
            "offset": offset or 0,
        }

    res = await wrapper(get)
    logger.debug(f"GetVoice - {res}")
    return res


async def get_track_info(ids: list):
    res = await wrapper(GetTrackDetail, ids)
    logger.debug(f"GetTrackDetail - {res}")
    return res


async def get_track_audio(song_ids: list, bit_rate=999999, encode_type="aac"):
    res = await wrapper(
        GetTrackAudio, song_ids, bitrate=bit_rate, encodeType=encode_type
    )
    logger.debug(f"GetTrackAudio - {res}")
    return res
