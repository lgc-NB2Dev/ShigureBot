import asyncio
from typing import Optional

from pydantic import BaseSettings

from config import init

config = None


class Config(BaseSettings):
    # Your Config Here
    token: Optional[str] = ''
    ignore_repos: Optional[list[Optional[str]]] = []

    class Config:
        extra = "ignore"


async def update_conf():
    global config
    config = await init(
        'blackbe',
        Config,
        {'token': '', 'ignore_repos': []}
    )


asyncio.get_event_loop().run_until_complete(update_conf())
