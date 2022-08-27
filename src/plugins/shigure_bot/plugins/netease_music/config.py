import asyncio
from typing import Optional

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    login: bool
    ct_code: str
    phone: str
    pwd: str
    fake_ip: Optional[str]
    list_limit: int


async def update_conf():
    global config
    config = await init(
        "netease_music",
        ConfigModel,
        {
            "login": False,
            "ct_code": "86",
            "phone": "",
            "pwd": "",
            "fake_ip": None,
            "list_limit": 10
        },
    )


asyncio.run(update_conf())
