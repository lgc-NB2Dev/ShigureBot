import asyncio

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    proxy: str = ""
    group_forward: bool = True
    saucenao_key: str = ""
    max_num: int


async def update_conf():
    global config
    config = await init(
        "pic_search",
        ConfigModel,
        {
            "proxy": "http://127.0.0.1:10809",
            "group_forward": True,
            "saucenao_key": "",
            "max_num": 2
        },
    )


asyncio.run(update_conf())
