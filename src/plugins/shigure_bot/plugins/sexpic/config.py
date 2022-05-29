import asyncio

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    only_private: bool
    trigger_words: list[str]
    delay: int
    proxy: str
    withdraw_delay: int
    send_details: bool
    can_filter_by_tag: bool


async def update_conf():
    global config
    config = await init(
        'sexpic',
        ConfigModel,
        {'only_private'     : False,
         'trigger_words'    : ['色图', '涩图', '瑟图', '二次元', '二刺猿', '二刺螈'],
         'delay'            : 120,
         'proxy'            : 'http://127.0.0.1:10809',
         'withdraw_delay'   : 0,
         'send_details'     : True,
         'can_filter_by_tag': True}
    )


asyncio.get_event_loop().run_until_complete(update_conf())
