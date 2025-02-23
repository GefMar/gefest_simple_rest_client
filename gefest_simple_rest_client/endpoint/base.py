__all__ = ("BaseEndpoint",)

from abc import ABC, abstractmethod
import typing
from urllib import parse as urlparse

from aiohttp import ClientResponse
from requests import Response

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

    def get(self, *, path_params: PathParamsT = None, query_params: dict | None = None) -> Response:
        return self.client.safe_request("GET", self.url(path_params), params=query_params)

    async def get_async(self, *, path_params: dict | None = None, query_params: dict | None = None) -> ClientResponse:
        return await self.client.safe_request_async("GET", self.url(path_params), params=query_params)

    def post(
        self, *, path_params: PathParamsT = None, query_params: dict | None = None, data: dict | None = None
    ) -> Response:
        return self.client.safe_request("POST", self.url(path_params), params=query_params, json=data)

    async def post_async(
        self, *, path_params: PathParamsT = None, query_params: dict | None = None, data: dict | None = None
    ) -> ClientResponse:
        return await self.client.safe_request_async("POST", self.url(path_params), params=query_params, json=data)

    def put(
        self, *, path_params: PathParamsT = None, query_params: dict | None = None, data: dict | None = None
    ) -> Response:
        return self.client.safe_request("PUT", self.url(path_params), params=query_params, json=data)

    async def put_async(
        self, *, path_params: PathParamsT = None, query_params: dict | None = None, data: dict | None = None
    ) -> ClientResponse:
        return await self.client.safe_request_async("PUT", self.url(path_params), params=query_params, json=data)

    def patch(
        self, *, path_params: PathParamsT = None, query_params: dict | None = None, data: dict | None = None
    ) -> Response:
        return self.client.safe_request("PATCH", self.url(path_params), params=query_params, json=data)

    async def patch_async(
        self, *, path_params: PathParamsT = None, query_params: dict | None = None, data: dict | None = None
    ) -> ClientResponse:
        return await self.client.safe_request_async("PATCH", self.url(path_params), params=query_params, json=data)

    def delete(self, *, path_params: PathParamsT = None, query_params: dict | None = None) -> Response:
        return self.client.safe_request("DELETE", self.url(path_params), params=query_params)
