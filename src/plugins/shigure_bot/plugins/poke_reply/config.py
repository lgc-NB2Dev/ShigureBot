import asyncio
import os
from typing import Optional

from pydantic import BaseModel

from config import BaseConfig, init

config = None


class Config(BaseConfig):
    async def get(self):
        if not self._tmp:
            tmp = await super(Config, self).get()
            for i in tmp.copy():
                if i.type == 'image_folder':
                    tmp.remove(i)
                    for n in find_all_file(i.content):
                        tmp.append(Reply(type='image', content=n, action=i.action))
            self._tmp = tmp
        return self._tmp


class Reply(BaseModel):
    type: str
    content: str
    action: Optional[bool]


def find_all_file(base):
    li = []
    for root, ds, fs in os.walk(base):
        for f in fs:
            fullname = os.path.join(root, f)
            li.append(fullname)
    return li


async def update_conf():
    global config
    config = await init(
        'poke_replies',
        Reply,
        [],
        cls=Config
    )


asyncio.get_event_loop().run_until_complete(update_conf())
