from typing import List, Optional

from nonebot.adapters.onebot.v11 import Message, MessageSegment
from pydantic import BaseModel


class BlackBEReturnDataFullInfo(BaseModel):
    area_code: str
    black_id: str
    info: str
    is_user: bool
    level: int
    name: str
    phone: str
    photos: List[str]
    qq: int
    server: str
    time: str
    uuid: str
    xuid: str


class BlackBEReturnDataInfo(BaseModel):
    uuid: str
    name: str
    black_id: Optional[str]
    xuid: str
    info: str
    server: Optional[str]
    time: Optional[str]
    level: int
    qq: int
    area_code: Optional[str]
    phone: Optional[int]
    photos: Optional[List[Optional[str]]]


class BlackBEReturnData(BaseModel):
    repo_success: Optional[bool]
    repo_uuid: Optional[str]
    exist: bool
    info: List[Optional[BlackBEReturnDataInfo]]


class BlackBEReturnRepo(BaseModel):
    uuid: str
    name: str
    type: int
    list_num: int
    server: str
    server_type: str


class BlackBEReturnRepoList(BaseModel):
    repositories_num: int
    repositories_list: List[Optional[BlackBEReturnRepo]]


class BlackBEReturn(BaseModel):
    success: bool
    status: int
    message: str
    version: str
    codename: str
    time: str
    data: (
        BlackBEReturnData
        | List[BlackBEReturnData]
        | BlackBEReturnRepoList
        | BlackBEReturnDataFullInfo
        | List[None]
    )


class ForwardMsg(list[Message]):
    def append(self, obj):
        super(ForwardMsg, self).append(
            Message(MessageSegment.text(obj) if isinstance(obj, str) else obj)
        )

    def extend(self, iterable):
        for i in iterable:
            self.append(i)

    def get_msg(self, sender_name, sender_uin):
        return [
            {
                "type": "node",
                "data": {
                    "name": sender_name,
                    "uin": sender_uin,
                    "content": [{"type": y.type, "data": y.data} for y in x],
                },
            }
            for x in self
        ]
