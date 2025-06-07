__all__ = ("ClientOptions", "RequestOptions")

from collections.abc import Callable, Mapping
import ssl
from typing import Any, TypedDict

from httpx import _client, _types
from httpx._config import Limits
from httpx._transports.base import AsyncBaseTransport


class ClientOptions(TypedDict, total=False):
    cookies: _types.CookieTypes | None
    verify: ssl.SSLContext | str | bool
    cert: _types.CertTypes | None
    http1: bool
    http2: bool
    proxy: _types.ProxyTypes | None
    mounts: None | Mapping[str, AsyncBaseTransport | None]
    timeout: _types.TimeoutTypes
    follow_redirects: bool
    limits: Limits
    max_redirects: int
    event_hooks: None | Mapping[str, list[_client.EventHook]]
    transport: AsyncBaseTransport | None
    trust_env: bool
    default_encoding: str | Callable[[bytes], str]
    auth: _types.AuthTypes | None
    headers: dict[str, str] | None


class RequestOptions(TypedDict, total=False):
    params: _types.QueryParamTypes | None
    headers: dict[str, str] | None
    cookies: _types.CookieTypes | None
    verify: ssl.SSLContext | str | bool
    cert: _types.CertTypes | None
    http1: bool
    http2: bool
    proxy: _types.ProxyTypes | None
    mounts: None | Mapping[str, AsyncBaseTransport | None]
    timeout: _types.TimeoutTypes | _client.UseClientDefault
    follow_redirects: bool | _client.UseClientDefault
    limits: Limits
    max_redirects: int
    event_hooks: None | Mapping[str, list[_client.EventHook]]
    transport: AsyncBaseTransport | None
    trust_env: bool
    default_encoding: str | Callable[[bytes], str]
    content: _types.RequestContent | None
    data: _types.RequestData | None
    files: _types.RequestFiles | None
    json: Any | None
    extensions: _types.RequestExtensions | None
    auth: _types.AuthTypes | _client.UseClientDefault | None
