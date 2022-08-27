import asyncio

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    send_link: bool


async def update_conf():
    global config
    config = await init("hitokoto", ConfigModel, {"send_link": True})


asyncio.run(update_conf())
