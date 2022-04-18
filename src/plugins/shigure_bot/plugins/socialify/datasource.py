from os import getcwd

from aiohttp import ClientSession
from nonebot_plugin_htmlrender import get_new_page
from playwright.async_api import Page

from .utils import parse_dict


async def get_cover(repo, **kwargs):
    async with ClientSession() as s:
        async with s.get(f'https://socialify.git.ci/{repo}/image', params=parse_dict(
                {'description'        : kwargs.get('description', 1),
                 'descriptionEditable': kwargs.get('descriptionEditable', None),
                 'font'               : kwargs.get('font', None),
                 'forks'              : kwargs.get('forks', 1),
                 'issues'             : kwargs.get('issues', 1),
                 'language'           : kwargs.get('language', 1),
                 'logo'               : kwargs.get('logo', None),
                 'name'               : kwargs.get('name', 1),
                 'owner'              : kwargs.get('owner', 1),
                 'pattern'            : kwargs.get('pattern', None),
                 'pulls'              : kwargs.get('pulls', 1),
                 'stargazers'         : kwargs.get('stargazers', 1),
                 'theme'              : kwargs.get('theme', None)}
        )) as resp:
            if not resp.status == 200:
                raise Exception(await resp.text())
            ret = await resp.text()

    async with get_new_page() as page:  # type: Page
        await page.goto(f'file://{getcwd()}')
        await page.set_content(ret, wait_until="networkidle")
        img = await page.locator('svg').screenshot()

    return img
