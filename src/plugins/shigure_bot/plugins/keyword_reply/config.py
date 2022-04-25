import asyncio
from typing import List

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    type: str
    to_me: bool
    keywords: List[str]
    replies: List[str]


async def update_conf():
    global config
    config = await init(
        'keyword_replies',
        ConfigModel,
        []
    )


asyncio.get_event_loop().run_until_complete(update_conf())
