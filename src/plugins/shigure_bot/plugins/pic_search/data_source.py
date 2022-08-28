import time
from io import BytesIO
from typing import BinaryIO, Optional

import httpx
from saucenao_api import AIOSauceNao
from saucenao_api.containers import SauceResponse
from saucenao_api.errors import (
    BadFileSizeError,
    BadKeyError,
    LongLimitReachedError,
    ShortLimitReachedError,
    UnknownApiError,
)

from .config import config


class ProxiedAIOSauceNao(AIOSauceNao):
    def __init__(self, *args, proxy=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy = proxy

    async def __aenter__(self):
        self._session = httpx.AsyncClient()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.aclose()

    async def from_file(
        self, file: tuple[Optional[str], BinaryIO, str]
    ) -> SauceResponse:
        return await super().from_file(file)  # noqa

    async def _search(self, params, files=None):
        session = self._session or httpx.AsyncClient(proxies=self.proxy)

        resp = await session.post(self.SAUCENAO_URL, params=params, files=files)
        status_code = resp.status_code

        # close only if not called via 'async with AIOSauceNao(...)'
        if not self._session:
            await session.aclose()

        if status_code == 200:
            parsed_resp = resp.json()
            raw = self._verify_response(parsed_resp, params)

            return SauceResponse(raw)

        # Taken from https://saucenao.com/tools/examples/api/identify_images_v1.1.py
        # Actually server returns 200 and user_id=0 if key is bad
        elif status_code == 403:
            raise BadKeyError("Invalid API key")

        elif status_code == 413:
            raise BadFileSizeError("File is too large")

        elif status_code == 429:
            parsed_resp = resp.json()
            if "Daily" in parsed_resp["header"]["message"]:
                raise LongLimitReachedError("24 hours limit reached")
            raise ShortLimitReachedError("30 seconds limit reached")

        raise UnknownApiError(f"Server returned status code {status_code}")


def get_timestamp():
    return round(time.time() * 1000)


async def down_pic(url, use_proxy=False):
    async with httpx.AsyncClient(
        proxies=(config.proxy or None) if use_proxy else None
    ) as s:
        r = await s.get(url)
        return r.read()


async def saucenao_search(url: str = None, pic: bytes = None, down_from_url=False):
    if (url and pic) or (not (url or pic)):
        raise ValueError("请仅提供一个参数")

    async with ProxiedAIOSauceNao(
        api_key=config.saucenao_key, proxy=config.proxy or None
    ) as sauce:
        if url:
            if down_from_url:
                pic = await down_pic(url)
            else:
                return await sauce.from_url(url)
        return await sauce.from_file(("pic.png", BytesIO(pic), "image/png"))
