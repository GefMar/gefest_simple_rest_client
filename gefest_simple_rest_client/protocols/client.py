__all__ = ("ClientProtocol",)

import typing

from aiohttp import ClientResponse
from requests import Response


class ClientProtocol(typing.Protocol):
    base_url: str
    headers: dict[str, str]

    def safe_request(self, method: str, url: str, **kwargs) -> Response: ...

    async def safe_request_async(self, method: str, url: str, **kwargs) -> ClientResponse: ...
