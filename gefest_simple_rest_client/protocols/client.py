__all__ = ("ClientProtocol",)

import typing

from httpx import Response


HeadersT = dict[str, str]


class ClientProtocol(typing.Protocol):
    base_url: str
    default_headers: typing.ClassVar[HeadersT]

    def make_headers(self, headers: HeadersT, *, update_default: bool = True) -> HeadersT: ...

    def safe_request(self, method: str, url: str, **kwargs) -> Response: ...

    async def safe_request_async(self, method: str, url: str, **kwargs) -> Response: ...
