"""这配置文件系统就一屎山……为了动态统一重载配置，能跑就行"""
import json
import os.path
from typing import Callable

import aiofiles
from nonebot import logger
from pydantic import BaseModel

tmp = []


class BaseConfig:
    def __init__(self, filename: str, model: Callable[[...], BaseModel] = None, default_conf: dict = None):
        self._filename = filename
        self._model = model
        self._default_conf = default_conf
        self._tmp = None

    async def get(self):
        if not self._tmp:
            cf = await self.load()
            if self._model:
                if isinstance(cf, dict):
                    self._tmp = self._model(**cf)
                elif isinstance(cf, (tuple, list, set)):
                    self._tmp = [self._model(**x) for x in cf]
                else:
                    raise TypeError('Type not supported')
            else:
                self._tmp = cf

        return self._tmp

    async def load(self):
        fpath = os.path.join('shigure', self._filename + '.json')
        dir_name = os.path.dirname(fpath)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        if not os.path.exists(fpath):
            conf = self._default_conf
        else:
            async with aiofiles.open(fpath, encoding='utf-8') as f:
                conf = json.loads(await f.read())

            if isinstance(conf, dict) and isinstance(self._default_conf, dict):
                # 将未配置的配置项配置为默认
                for k, v in self._default_conf.items():
                    if not k in conf:
                        conf[k] = v

        async with aiofiles.open(fpath, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(conf, indent=2, ensure_ascii=False))

        logger.debug(f'Loaded config "{self._filename}": {conf}')
        return conf

    def clear_tmp(self):
        self._tmp = None

    def _check_tmp_is_list(self):
        if not isinstance(self._tmp, list):
            raise TypeError

    def _check_tmp_is_model(self):
        if not isinstance(self._tmp, BaseModel):
            raise TypeError

    def __getattr__(self, item):
        self._check_tmp_is_model()
        return self._tmp.__getattribute__(item)

    def __getitem__(self, item):
        self._check_tmp_is_list()
        return self._tmp.__getitem__(item)

    def __len__(self):
        self._check_tmp_is_list()
        return len(self._tmp)

    def __iter__(self):
        self._check_tmp_is_list()
        yield from self._tmp


async def init(*args, cls: Callable[[...], BaseConfig] = None, **kwargs):
    if cls:
        conf = cls(*args, **kwargs)
    else:
        conf = BaseConfig(*args, **kwargs)
    tmp.append(conf)
    await conf.get()
    return conf


async def reload():
    for cf in tmp:
        cf.clear_tmp()
        await cf.get()
