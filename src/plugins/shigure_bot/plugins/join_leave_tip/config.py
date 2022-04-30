import asyncio

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    join_message: str
    leave_message: str


async def update_conf():
    global config
    config = await init(
        'join_leave_tip',
        ConfigModel,
        {'join_message' : '{at} 欢迎新入群的rbq~',
         'leave_message': '{nick}({qq})默默地离开了我们……'}
    )


asyncio.get_event_loop().run_until_complete(update_conf())
