__all__ = ("BaseEndpoint",)

from abc import ABC, abstractmethod
import typing
from urllib import parse as urlparse

from httpx import Response

from ..protocols.client import ClientProtocol
from ..types_stubs import RequestOptions
from .path_template import PathTemplate


_headers_key = "headers"
BaseClientT = typing.TypeVar("BaseClientT", bound=ClientProtocol)
PathTemplateT = typing.TypeVar("PathTemplateT", bound=PathTemplate)
PathParamsT = dict[str, typing.Any] | None


class BaseEndpoint(ABC, typing.Generic[BaseClientT, PathTemplateT]):  # noqa: WPS214
    ban_methods: frozenset = frozenset()
    default_headers: typing.ClassVar[dict[str, str]] = {}

    def __init__(self, client: BaseClientT):
        self.client: BaseClientT = client

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def path_template(self) -> PathTemplateT:
        raise NotImplementedError

    @property
    def headers(self) -> dict[str, str]:
        return self.client.make_headers(self.default_headers)

    def formated_path(self, path_params: PathParamsT) -> str:
        if path_params is None:
            path_params = {}
        return self.path_template.format(path_params)

    def url(self, path_params: PathParamsT) -> str:
        base_url = self.client.base_url.rstrip("/")
        path = self.formated_path(path_params)
        return urlparse.urljoin(f"{base_url}/", path)

    def request(self, method: str, *, path_params: PathParamsT = None, **kwargs: RequestOptions) -> Response:
        if _headers_key not in kwargs:
            kwargs[_headers_key] = self.headers  # type: ignore[assignment]
        return self.client.safe_request(method, self.url(path_params), **kwargs)

    async def request_async(
        self, method: str, *, path_params: PathParamsT = None, **kwargs: RequestOptions
    ) -> Response:
        if _headers_key not in kwargs:
            kwargs[_headers_key] = self.headers  # type: ignore[assignment]
        return await self.client.safe_request_async(method, self.url(path_params), **kwargs)

    def get(self, **kwargs) -> Response:
        return self.request("GET", **kwargs)

    async def get_async(self, **kwargs) -> Response:
        return await self.request_async("GET", **kwargs)

    def post(self, **kwargs) -> Response:
        return self.request("POST", **kwargs)

    async def post_async(self, **kwargs) -> Response:
        return await self.request_async("POST", **kwargs)

    def put(self, **kwargs) -> Response:
        return self.request("PUT", **kwargs)

    async def put_async(self, **kwargs) -> Response:
        return await self.request_async("PUT", **kwargs)

    def patch(self, **kwargs) -> Response:
        return self.request("PATCH", **kwargs)

    async def patch_async(self, **kwargs) -> Response:
        return await self.request_async("PATCH", **kwargs)

    def delete(self, **kwargs) -> Response:
        return self.request("DELETE", **kwargs)

    async def delete_async(self, **kwargs) -> Response:
        return await self.request_async("DELETE", **kwargs)
