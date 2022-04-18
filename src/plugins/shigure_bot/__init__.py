import pkgutil
import sys
from pathlib import Path

from nonebot import load_plugin

except_plugins = ['config']

path = str((Path(__file__).parent / "plugins").
           resolve())
sys.path.append(path)

for pl in pkgutil.iter_modules([path]):
    if pl.name not in except_plugins:
        load_plugin(pl.name)

__version__ = '0.1.3'
