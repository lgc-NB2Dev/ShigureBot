import asyncio
from typing import Optional

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    token: Optional[str] = ''
    ignore_repos: Optional[list[Optional[str]]] = []


async def update_conf():
    global config
    config = await init(
        'blackbe',
        ConfigModel,
        {'token': '', 'ignore_repos': []}
    )


asyncio.get_event_loop().run_until_complete(update_conf())
