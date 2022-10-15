import asyncio

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    tg_bot_token: str
    tg_chats: dict[str, int]
    proxy: str


async def update_conf():
    global config
    config = await init(
        "tg_sync",
        ConfigModel,
        {"tg_bot_token": "", "tg_chats": {}, "proxy": ""},
    )


asyncio.run(update_conf())
