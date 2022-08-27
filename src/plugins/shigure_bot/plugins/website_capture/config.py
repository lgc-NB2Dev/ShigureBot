import asyncio

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    ignore_sites: list[str]


async def update_conf():
    global config
    config = await init(
        "website_capture", ConfigModel, {"ignore_sites": ["xvideos.com", "pornhub.com"]}
    )


asyncio.run(update_conf())
