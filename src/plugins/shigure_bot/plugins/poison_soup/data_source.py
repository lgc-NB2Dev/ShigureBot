import asyncio
import os
import random

import aiofiles

soup = []


def get_soup():
    return random.choice(soup)


async def load_soup():
    global soup
    async with aiofiles.open(
        os.path.join(os.path.dirname(__file__), "soup.txt"), encoding="utf-8"
    ) as f:
        soup = [x.strip() for x in await f.readlines()]


asyncio.get_event_loop().run_until_complete(load_soup())
