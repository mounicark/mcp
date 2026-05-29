
import httpx
from mcp import types

async def fetch(url: str) -> list[types.ContentBlock]:
    headers = {
        "User-Agent": "Website fetcher MCP"
    }

    async with httpx.AsyncClient(headers=headers) as client:
        response = client.get(url, timeout=20)

    response.raise_for_status()

    return [
        types.TextContent(
            type="text",
            text=response.text
        )
    ]

