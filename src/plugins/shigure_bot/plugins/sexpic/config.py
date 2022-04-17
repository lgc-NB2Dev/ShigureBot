import asyncio

from pydantic import BaseSettings

from config import init

config = None


class Config(BaseSettings):
    only_private: bool
    trigger_words: list[str]
    delay: int

    class Config:
        extra = "ignore"


async def update_conf():
    global config
    config = await init(
        'sexpic',
        Config,
        {'only_private': False, 'trigger_words': ['色图', '涩图', '瑟图', '二次元', '二刺猿', '二刺螈'], 'delay': 120}
    )


asyncio.get_event_loop().run_until_complete(update_conf())
