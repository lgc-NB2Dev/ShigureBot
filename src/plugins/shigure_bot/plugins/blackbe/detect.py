from nonebot import logger

from .config import config as conf
from .datatypes import BlackBEReturn
from .get_data import get_simple_info

_ret_template = BlackBEReturn(
    **{
        "success": True,
        "status": 2001,
        "message": "用户不存在于黑名单中哦",
        "version": "v3",
        "codename": "Moriya Suwako",
        "time": 0,
        "data": {"exist": False, "info": []},
    }
)


class BlackBEDetect:
    tmp_black: dict = {}
    tmp_noticed: dict = {}

    def __init__(self):
        pass

    def set_notice_object(self, group):
        if not self.tmp_noticed.get(group):
            self.tmp_noticed[group] = {}

    def has_noticed(self, group, qq):
        self.set_notice_object(group)
        return self.tmp_noticed[group].get(qq) == True

    def set_notice_stat(self, group, qq, stat):
        self.set_notice_object(group)
        self.tmp_noticed[group][qq] = stat

    async def detect(self, qq):
        if (ret := self.tmp_black.get(qq)) is None:
            self.tmp_black[qq] = _ret_template  # 避免同时间多次访问
            ret = await get_simple_info(token=conf.token, qq=qq)
            if isinstance(ret, Exception):
                logger.opt(exception=ret).exception("查询云黑记录失败")
                ret = None
            self.tmp_black[qq] = ret
        return ret
