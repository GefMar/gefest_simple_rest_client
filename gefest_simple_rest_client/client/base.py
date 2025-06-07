from abc import ABC, abstractmethod
import time
import typing

import httpx

from ..endpoint.base import BaseEndpoint
from ..types_stubs import ClientOptions, RequestOptions


BaseEndpointT = typing.TypeVar("BaseEndpointT", bound=BaseEndpoint)


class BaseClient(ABC, typing.Generic[BaseEndpointT]):  # noqa: WPS214
    endpoints: typing.Iterable[type[BaseEndpointT]] = []
    default_headers: typing.ClassVar[dict[str, str]] = {}

    def __init__(self, *, session_timeout: int = 300, client_options: ClientOptions | None = None):
        if not self.endpoints:
            msg = "`endpoints` must be defined in the client class"
            raise NotImplementedError(msg)
        self.session_timeout = session_timeout
        self.client_options = client_options or {}
        self._sync_client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None
        self._last_session_access_time = time.time()

        self._initialize_endpoints()

    def __getattr__(self, item: str) -> BaseEndpointT:
        for endpoint_class in self.endpoints:
            if item == str(endpoint_class.name).lower():
                return getattr(self, item)
        msg = f"{self.__class__.__name__!r} has no attribute {item!r}"
        raise AttributeError(msg)

    def __enter__(self) -> "BaseClient":
        self._create_sync_client()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close_sync_client()

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

    def make_headers(self, headers: dict[str, str], *, update_default: bool = True) -> dict[str, str]:
        if update_default:
            return {**self.default_headers, **headers}
        return headers

    def safe_request(self, method: str, url: str, **kwargs: RequestOptions) -> httpx.Response:
        client = self._get_sync_client()
        return client.request(method, url, **kwargs)

    def close_sync_client(self):
        if self._sync_client is not None:
            self._sync_client.close()

    async def safe_request_async(self, method: str, url: str, **kwargs: RequestOptions) -> httpx.Response:
        client = await self._get_async_client()
        return await client.request(method, url, **kwargs)

    async def close_async_client(self):
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None

    def _get_sync_client(self) -> httpx.Client:
        if self._sync_client is None or (time.time() - self._last_session_access_time) > self.session_timeout:
            self._create_sync_client()
        self._last_session_access_time = time.time()
        return self._sync_client

    def _create_sync_client(self):
        self.close_sync_client()
        self._sync_client = httpx.Client(**self._make_client_options())

    async def _get_async_client(self) -> httpx.AsyncClient:
        if self._async_client is None or (time.time() - self._last_session_access_time) > self.session_timeout:
            await self._create_async_client()
        self._last_session_access_time = time.time()
        return self._async_client

    async def _create_async_client(self):
        await self.close_async_client()
        self._async_client = httpx.AsyncClient(**self._make_client_options())

    def _initialize_endpoints(self):
        for endpoint_class in self.endpoints:
            endpoint_instance = endpoint_class(self)
            setattr(self, endpoint_instance.name.lower(), endpoint_instance)

    def _make_client_options(self) -> ClientOptions:
        headers = self.client_options.get("headers")
        return self.client_options | {"headers": self.make_headers(headers or {})}
