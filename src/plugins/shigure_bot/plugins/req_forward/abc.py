from typing import Any

from nonebot import logger
from nonebot.adapters.onebot.v11 import FriendRequestEvent, GroupRequestEvent


class ReqDict(dict):
    last_req: FriendRequestEvent | GroupRequestEvent = None

    def setitem(self, key: str, value: FriendRequestEvent | GroupRequestEvent):
        is_fri = isinstance(value, FriendRequestEvent)
        last_req_is_fri = isinstance(self.last_req, FriendRequestEvent)

        for k, flag in self.items():
            if value.flag == flag.flag or value.flag == self.last_req.flag:
                logger.info(f'重复flag的请求事件：{value}')
                return

            if is_fri:
                if (isinstance(flag, FriendRequestEvent) and value.user_id == flag.user_id) or \
                        (last_req_is_fri and self.last_req.user_id == flag.user_id):
                    logger.info(f'重复用户的好友请求：{value}')
                    self.__setitem__(k, value)
                    return
            else:
                if (isinstance(flag, GroupRequestEvent) and value.group_id == flag.group_id) or \
                        (not last_req_is_fri and self.last_req.group_id == flag.group_id):
                    logger.info(f'重复群号的邀请进群请求：{value}')
                    self.__setitem__(k, value)
                    return
        self.__setitem__(key, value)
        return True

    def pop(self, **kwargs) -> Any:
        self.last_req = super().pop(**kwargs)
        return self.last_req
