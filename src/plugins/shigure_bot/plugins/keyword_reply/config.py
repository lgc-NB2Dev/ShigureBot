import asyncio
from typing import Literal, Optional

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    type: Literal["full", "fuzzy", "regex"]
    to_me: Optional[bool] = False
    keywords: list[str]
    replies: list[str | list[dict]]
    ignore_case: Optional[bool] = True


async def update_conf():
    global config
    config = await init("keyword_replies", ConfigModel, [])


asyncio.run(update_conf())
