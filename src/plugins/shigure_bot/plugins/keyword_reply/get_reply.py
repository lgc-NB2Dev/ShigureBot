import random
import re

from .config import config as conf


async def get_reply(msg: str, to_me: bool):
    for reply in conf:
        if reply.to_me:
            if not to_me:
                continue

        if reply.type == 'full':
            matcher = lambda m, kw: m == kw
        elif reply.type == 'fuzzy':
            matcher = lambda m, kw: m.find(kw) != -1
        elif reply.type == 'regex':
            matcher = lambda m, kw: re.fullmatch(kw, m) is not None
        else:
            matcher = lambda _, __: False

        for kwd in reply.keywords:
            if matcher(msg.lower().strip(), kwd.lower().strip()):
                return random.choice(reply.replies)
