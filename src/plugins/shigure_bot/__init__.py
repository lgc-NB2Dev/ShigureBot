import sys
from pathlib import Path

import nonebot

path = str((Path(__file__).parent / "plugins").
           resolve())

sys.path.append(path)

_sub_plugins = set()
_sub_plugins |= nonebot.load_plugins(path)

__version__ = '0.1.2'
