from nonebot import logger
from nonebot.adapters.onebot.v11 import FriendRequestEvent, GroupRequestEvent


class ReqDict(dict):
    def setitem(self, key: str, value: FriendRequestEvent | GroupRequestEvent):
        for flag in self.values():
            if value.flag == flag:
                logger.info(f'重复flag的请求事件：{value}')
                return
        self.__setitem__(key, value)
        return True
