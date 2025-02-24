__all__ = ("BaseEndpoint",)

from abc import ABC, abstractmethod
import typing
from urllib import parse as urlparse

from httpx import Response

from ..protocols.client import ClientProtocol
from .path_template import PathTemplate


BaseClientT = typing.TypeVar("BaseClientT", bound=ClientProtocol)
PathTemplateT = typing.TypeVar("PathTemplateT", bound=PathTemplate)
PathParamsT = dict[str, typing.Any] | None


class BaseEndpoint(ABC, typing.Generic[BaseClientT, PathTemplateT]):  # noqa: WPS214
    ban_methods: frozenset = frozenset()

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

    def formated_path(self, path_params: PathParamsT) -> str:
        if path_params is None:
            path_params = {}
        return self.path_template.format(path_params)

    def url(self, path_params: PathParamsT) -> str:
        base_url = self.client.base_url.rstrip("/")
        path = self.formated_path(path_params)
        return urlparse.urljoin(f"{base_url}/", path)

    def request(
        self,
        method: str,
        *,
        path_params: PathParamsT = None,
        query_params: dict | None = None,
        data: dict | None = None,
    ) -> Response:
        return self.client.safe_request(method, self.url(path_params), params=query_params, json=data)

    async def request_async(
        self,
        method: str,
        *,
        path_params: PathParamsT = None,
        query_params: dict | None = None,
        data: dict | None = None,
    ) -> Response:
        return await self.client.safe_request_async(method, self.url(path_params), params=query_params, json=data)

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
