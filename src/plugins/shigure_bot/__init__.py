import os.path
import pkgutil
import sys

from nonebot import load_plugin

preloads = ['config']

path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'plugins'))
sys.path.append(path)

for pl in preloads:
    load_plugin(pl)
for pl in pkgutil.iter_modules([path]):
    if pl.name not in preloads:
        load_plugin(pl.name)
