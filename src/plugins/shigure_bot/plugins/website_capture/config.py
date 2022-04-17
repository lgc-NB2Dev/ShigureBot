import asyncio

from pydantic import BaseSettings

from config import init

config = None


class Config(BaseSettings):
    ignore_sites: list[str]

    class Config:
        extra = "ignore"


async def update_conf():
    global config
    config = await init(
        'website_capture',
        Config,
        {'ignore_sites': ['xvideos.com', 'pornhub.com']}
    )


asyncio.get_event_loop().run_until_complete(update_conf())
