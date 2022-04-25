import asyncio

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    auto_allow_superusers: bool
    forward_friend_req: bool
    forward_group_invite: bool


async def update_conf():
    global config
    config = await init(
        'req_foward',
        ConfigModel,
        {'auto_allow_superusers': True,
         'forward_friend_req'   : True,
         'forward_group_invite' : True}
    )


asyncio.get_event_loop().run_until_complete(update_conf())
