import os.path

import aiofiles
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_htmlrender import md_to_pic

from .config import config as conf
from .datatypes import BlackBEReturnDataInfo
from .get_data import *


def parse_lvl(lvl: int):
    if lvl == 1:
        msg = '有作弊行为，但未对其他玩家造成实质上损害'
    elif lvl == 2:
        msg = '有作弊行为，且对玩家造成一定的损害'
    elif lvl == 3:
        msg = '严重破坏服务器，对玩家和服务器造成较大的损害'
    else:
        msg = '未知'
    return f'等级{lvl}（{msg}）'


async def parse_info(info: BlackBEReturnDataInfo, uuid=''):
    async def get_repo_name(_uuid):
        if _uuid == '1':
            return '公有库（1）'
        else:
            n = await get_repo_detail(_uuid, conf.token)
            return f'{n.name if n else "未知"}（{_uuid}）'

    black_id = info.black_id if info.black_id else uuid
    repo_name = await get_repo_name(black_id)

    photos = None
    if info.photos:
        photos = '\n- 证据图片：\n\n'
        for photo in info.photos:
            path = './shigure/blackbe_tmp'
            name = photo[photo.rfind('/') + 1:]
            full_path = os.path.join(path, name)

            if not os.path.exists(path):
                os.makedirs(path)

            if os.path.exists(full_path):
                photos += f'  ![]({os.path.abspath(full_path)})\n\n'
            else:
                if not photo.startswith('http://') or photo.startswith('https://'):
                    photo = 'http://' + photo
                try:
                    async with aiohttp.ClientSession() as s:
                        async with s.get(photo) as raw:
                            p = await raw.read()
                    async with aiofiles.open(full_path, 'wb') as f:
                        await f.write(p)
                except:
                    photos += f'  获取图片失败（{photo}）\n\n'
                else:
                    photos += f'  ![]({os.path.abspath(full_path)})\n\n'

    return '\n'.join([  # nmd 用括号隐式连接的时候格式化抽风了
        f'- 玩家ID：{info.name}\n',
        f'- 危险等级：{parse_lvl(info.level)}\n',
        f'- 记录原因：{info.info}\n',
        (f'- 违规服务器：{info.server}\n' if info.server else ''),
        f'- XUID：{info.xuid}\n',
        f'- 玩家QQ：{info.qq}\n',
        (f'- 玩家电话：{info.area_code} {info.phone}\n' if info.phone else ''),
        f'- 库来源：{repo_name}\n',
        (f'- 记录时间：{info.time}\n' if info.time else ''),
        f'- 记录UUID：{info.uuid}',
        photos if photos else ''])


async def get_info_msg(**kwargs):
    ret_simple = await get_simple_info(**kwargs)
    ret_repo = None
    if conf.token:
        ret_repo = await get_private_repo_info(conf.token, conf.ignore_repos, **kwargs)
    info = []
    tip_success = []
    tip_fail = []

    if isinstance(ret_simple, BlackBEReturn):
        if ret_simple.success:
            if ret_simple.data.exist:
                tip_success.append(f' {len(ret_simple.data.info)} 条公有库记录')
                for i in ret_simple.data.info:
                    t = await parse_info(i)
                    info.append(t)
        else:
            tip_fail.append(f'查询公有库记录失败：[{ret_simple.status}] {ret_simple.message}')
    else:
        tip_fail.append(f'查询公有库记录失败：{ret_simple!r}')

    if ret_repo:
        if isinstance(ret_repo, BlackBEReturn):
            if ret_repo.success:
                count = 0
                for i in ret_repo.data:
                    for n in i.info:
                        t = await parse_info(n, i.repo_uuid)
                        info.append(t)
                        count += 1
                if count:
                    tip_success.append(f' {len(ret_repo.data)} 个私有库的 {count} 条私有库记录')
            else:
                tip_fail.append(f'查询私有库记录失败：[{ret_repo.status}] {ret_repo.message}')
        else:
            tip_fail.append(f'查询私有库记录失败：{ret_repo!r}')

    msg = [f'# 关于 {list(kwargs.values())[0]} 的查询结果：']
    if tip_success:
        msg.append(f'查询到{"，".join(tip_success)}')
    if tip_fail:
        msg.extend(tip_fail)
    if not tip_success and not tip_fail:
        msg.append('没有查询到任何记录')
    for i in info:
        msg.append('----')
        msg.append(i)
    img = await md_to_pic('\n\n'.join(msg), width=1000)
    return MessageSegment.image(img)
