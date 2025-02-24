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

## Usage Example
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

## Feedback
If you have any questions or suggestions, feel free to reach out via [GitHub Issues](https://github.com/GefMar/gefest_simple_rest_client/issues).
