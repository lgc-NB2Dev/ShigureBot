import aiohttp
import nonebot

from .datatypes import BlackBEReturn

tmp_repos = {}


async def get_simple_info(token='', **kwargs):
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(
                    'https://api.blackbe.xyz/openapi/v3/check',
                    params=kwargs,
                    headers={'Authorization': f'Bearer {token}'} if token else None
            ) as raw:
                ret = await raw.json()
        return BlackBEReturn(**ret)
    except Exception as e:
        nonebot.logger.opt().error('查询失败')
        return e


async def get_private_repo_info(token, ignore_repos=None, **kwargs):
    try:
        repos = await get_repos(token)
        repos = [x.uuid for x in repos.data.repositories_list]
        if ignore_repos:
            for i in ignore_repos:
                try:
                    repos.remove(i)
                except:
                    pass

        async with aiohttp.ClientSession() as s:
            async with s.post(
                    'https://api.blackbe.xyz/openapi/v3/check/private',
                    params=kwargs,
                    headers={'Authorization': f'Bearer {token}'},
                    json={'repositories_uuid': repos}
            ) as raw:
                ret = await raw.json()
        return BlackBEReturn(**ret)
    except Exception as e:
        nonebot.logger.opt().error('查询失败')
        return e


async def get_repos(token):
    if token:
        global tmp_repos
        async with aiohttp.ClientSession() as s:
            async with s.get(
                    'https://api.blackbe.xyz/openapi/v3/private/repositories/list',
                    headers={'Authorization': f'Bearer {token}'}
            ) as raw:
                repos = await raw.json()
                repos = BlackBEReturn(**repos)
                tmp_repos = {x.uuid: x for x in repos.data.repositories_list}
        return repos


async def get_repo_detail(uuid, token):
    ret = tmp_repos.get(uuid)
    if not ret:
        await get_repos(token)
        ret = tmp_repos.get(uuid)
    return ret
