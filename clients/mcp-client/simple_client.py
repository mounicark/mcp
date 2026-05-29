import anyio

from mcp.client.streamable_http import streamable_http_client 
from mcp import ClientSession

async def main():
    async with streamable_http_client("http://127.0.0.1:8000") as (read, write):
        async with ClientSession



if __name__ == "__main__":
    anyio.run(main)
