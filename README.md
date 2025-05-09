# Gefest Simple REST Client

## Description
**Gefest Simple REST Client** is a library designed to simplify the creation of REST API clients in Python. Built on `httpx`, it provides both synchronous and asynchronous API interaction.

## Features
- 🛠️ Abstraction of clients and endpoints
- ⚙️ Support for both synchronous (`httpx.Client`) and asynchronous (`httpx.AsyncClient`) request models
- ✅ Dynamic access to endpoints
- ✨ URL templates for handling path parameters

## Installation
```sh
pip install gefest_simple_rest_client
```

## Simple Usage Example
```python
from gefest_simple_rest_client.client import BaseClient
from gefest_simple_rest_client.endpoint import BaseEndpoint, PathTemplate

class MyEndpoint(BaseEndpoint):
    name = "example"
    path_template = PathTemplate("/example/{id:int}")

class MyClient(BaseClient):
    base_url = "https://api.example.com"
    headers = {"Authorization": "Bearer YOUR_TOKEN"}
    endpoints = [MyEndpoint]

client = MyClient()
```

### Synchronous Usage
```python
response = client.example.get(path_params={"id": 123})
print(response.json())
```

### Asynchronous Usage
```python
import asyncio

async def fetch():
    async with MyClient() as client:
        response = await client.example.get_async(path_params={"id": 123})
        print(response.json())

asyncio.run(fetch())
```

## Errors when Passing Invalid Path Parameters
If incorrect parameters are provided, exceptions are raised:

```python
try:
    response = client.example.get(path_params={"id": "invalid_string"})
except Exception as e:
    print(f"Error: {e}")
```

Example error:
```
PathParamsValidationError: Parameter 'id' must be of type int
```

## Authorization
You can authorize requests in **three ways**: globally via headers, globally via `auth`, or per request.
### 1. Global Authorization via `headers`
You can define default authorization headers in the client.

```python
class MyClient(BaseClient):
    base_url = "https://example.com"
    default_headers = {
        "Authorization": "Bearer YOUR_TOKEN",
    }
    endpoints = [MyEndpoint]

client = MyClient()
response = client.example.get(path_params={"id": 1})
```
Request headers:
```pycon
>>> response.request.headers
Headers({
    'host': 'example.com',
    'user-agent': 'python-httpx/0.28.1',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate',
    'connection': 'keep-alive',
    'authorization': '[secure]',
})

>>> response.request.headers["authorization"]
'Bearer YOUR_TOKEN'
```

### 2. Global Authorization via `auth` parameter
You can pass an auth handler (e.g., tuple or httpx.Auth instance) when initializing the client:
```python
client = MyClient(client_options={"auth": ("username", "password")})
response = client.example.get(path_params={"id": 1})
```

Request headers:
```pycon
>>> response.request.headers["authorization"]
'Basic dXNlcm5hbWU6cGFzc3dvcmQ='
```

Or using a custom `Auth` class:
```python
from httpx import Auth, Request, Response

class BearerAuth(Auth):
    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request) -> typing.Generator[Request, Response, None]:
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request

client = MyClient(client_options={"auth": BearerAuth("your_token")})
response = client.example.get(path_params={"id": 1})
```

Request headers:
```pycon
>>> response.request.headers["authorization"]
'Bearer your_token'
```

### 3. Per-request Authorization
Even if a global authorization method is set, you can override it for a specific request using the auth argument:
```python
response = client.example.get(
    path_params={"id": 1},
    auth=("username", "password"),
)
```

Request headers:
```pycon
>>> response.request.headers["authorization"]
'Basic dXNlcm5hbWU6cGFzc3dvcmQ='
```

## Feedback
If you have any questions or suggestions, feel free to reach out via [GitHub Issues](https://github.com/GefMar/gefest_simple_rest_client/issues).
