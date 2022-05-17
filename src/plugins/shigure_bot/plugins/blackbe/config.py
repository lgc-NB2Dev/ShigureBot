import asyncio

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    token: str
    ignore_repos: list[str]
    use_group_forward_msg: bool


async def update_conf():
    global config
    config = await init(
        'blackbe',
        ConfigModel,
        {'token'                : '',
         'ignore_repos'         : [],
         'use_group_forward_msg': True}
    )


asyncio.get_event_loop().run_until_complete(update_conf())
