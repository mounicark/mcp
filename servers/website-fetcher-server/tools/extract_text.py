import httpx
from bs4 import BeautifulSoup
from mcp import types

async def extract_text(url: str) -> list[types.ContentBlock]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=20)

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(seperator='\n')

    return [
        types.TextContent(
            type="text",
            text=text[:10000]
        )
    ]

    