from abc import ABC, abstractmethod
import time
import typing

import aiohttp
import requests

from ..endpoint.base import BaseEndpoint


BaseEndpointT = typing.TypeVar("BaseEndpointT", bound=BaseEndpoint)


class BaseClient(ABC, typing.Generic[BaseEndpointT]):  # noqa: WPS214
    endpoints: typing.Iterable[type[BaseEndpointT]] = []

    def __init__(self, *, session_timeout=300):
        if not self.endpoints:
            msg = "`endpoints` must be defined in the client class"
            raise NotImplementedError(msg)
        self.session_timeout = session_timeout

        self._sync_session = requests.Session()
        self._async_session: aiohttp.ClientSession | None = None
        self._last_session_access_time = time.time()

        self._initialize_endpoints()

    def __getattr__(self, item: str) -> BaseEndpointT:
        for endpoint_class in self.endpoints:
            if item == str(endpoint_class.name).lower():
                return getattr(self, item)
        msg = f"{self.__class__.__name__!r} has no attribute {item!r}"
        raise AttributeError(msg)

    async def __aenter__(self) -> "BaseClient":
        await self._create_async_session()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.close_sync_session()
        await self.close_async_session()

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

    def safe_request(self, method: str, url: str, **kwargs) -> requests.Response:
        return self._sync_session.request(method, url, **kwargs)

    def close_sync_session(self):
        self._sync_session.close()

    async def safe_request_async(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        session = await self._get_async_session()
        return await session.request(method, url, **kwargs)

    async def close_async_session(self):
        if self._async_session:
            await self._async_session.close()
            self._async_session = None

    async def _get_async_session(self) -> aiohttp.ClientSession:
        if not self._async_session or (time.time() - self._last_session_access_time) > self.session_timeout:
            await self._create_async_session()
        self._last_session_access_time = time.time()
        return self._async_session

    async def _create_async_session(self):
        await self.close_async_session()
        self._async_session = aiohttp.ClientSession(headers=self.headers)

    def _initialize_endpoints(self):
        for endpoint_class in self.endpoints:
            endpoint_instance = endpoint_class(self)
            setattr(self, endpoint_instance.name.lower(), endpoint_instance)
