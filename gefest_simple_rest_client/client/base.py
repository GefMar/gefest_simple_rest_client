from abc import ABC, abstractmethod
import time
import typing

import httpx

from ..endpoint.base import BaseEndpoint


BaseEndpointT = typing.TypeVar("BaseEndpointT", bound=BaseEndpoint)


class BaseClient(ABC, typing.Generic[BaseEndpointT]):  # noqa: WPS214
    endpoints: typing.Iterable[type[BaseEndpointT]] = []

    def __init__(self, *, session_timeout=300):
        if not self.endpoints:
            msg = "`endpoints` must be defined in the client class"
            raise NotImplementedError(msg)
        self.session_timeout = session_timeout

        self._sync_client = httpx.Client()
        self._async_client: httpx.AsyncClient | None = None
        self._last_session_access_time = time.time()

        self._initialize_endpoints()

    def __getattr__(self, item: str) -> BaseEndpointT:
        for endpoint_class in self.endpoints:
            if item == str(endpoint_class.name).lower():
                return getattr(self, item)
        msg = f"{self.__class__.__name__!r} has no attribute {item!r}"
        raise AttributeError(msg)

    async def __aenter__(self) -> "BaseClient":
        await self._create_async_client()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.close_sync_client()
        await self.close_async_client()

    def __dir__(self) -> list[str]:  # noqa: WPS603
        base_attrs = list(super().__dir__())
        endpoint_names = [str(cls_endpoint.name).lower() for cls_endpoint in self.endpoints]
        return base_attrs + endpoint_names

    @property
    @abstractmethod
    def base_url(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def headers(self) -> dict:
        raise NotImplementedError

    def safe_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        return self._sync_client.request(method, url, **kwargs)

    def close_sync_client(self):
        self._sync_client.close()

    async def safe_request_async(self, method: str, url: str, **kwargs) -> httpx.Response:
        client = await self._get_async_client()
        return await client.request(method, url, **kwargs)

    async def close_async_client(self):
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    async def _get_async_client(self) -> httpx.AsyncClient:
        if not self._async_client or (time.time() - self._last_session_access_time) > self.session_timeout:
            await self._create_async_client()
        self._last_session_access_time = time.time()
        return self._async_client

    async def _create_async_client(self):
        await self.close_async_client()
        self._async_client = httpx.AsyncClient(headers=self.headers)

    def _initialize_endpoints(self):
        for endpoint_class in self.endpoints:
            endpoint_instance = endpoint_class(self)
            setattr(self, endpoint_instance.name.lower(), endpoint_instance)
