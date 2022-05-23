import asyncio

from pydantic import BaseModel

from .._config import init

config = None


class ConfigModel(BaseModel):
    join_message: str
    leave_message: str
    kick_message: str
    except_groups: list[int]


async def update_conf():
    global config
    config = await init(
        'join_leave_tip',
        ConfigModel,
        {'join_message' : '{at} 欢迎新入群的rbq~',
         'leave_message': '{nick}({qq})默默地离开了我们……',
         'kick_message' : '{nick}({qq})被至高无上的管理员{admin}制裁了！！（躲',
         'except_groups': []}
    )


asyncio.get_event_loop().run_until_complete(update_conf())
