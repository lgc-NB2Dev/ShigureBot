from pathlib import Path

from nonebot import load_plugins

path = str((Path(__file__).parent / "plugins").
           resolve())
# sys.path.append(path)

_sub = set()
_sub |= load_plugins(path)

__version__ = '0.3.1'
