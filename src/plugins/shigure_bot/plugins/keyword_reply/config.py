import asyncio
from typing import List

from pydantic import BaseModel

from config import init

config = None


class Reply(BaseModel):
    type: str
    to_me: bool
    keywords: List[str]
    replies: List[str]


async def update_conf():
    global config
    config = await init(
        'keyword_replies',
        Reply,
        []
    )


asyncio.get_event_loop().run_until_complete(update_conf())
