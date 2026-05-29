import anyio

from mcp.client.streamable_http import streamable_http_client 
# def manage_tools():
#     pass

# def llm():
#     pass

# def chat_loop():
#     pass

async def main():
    async with streamable_http_client()


if __name__ == "__main__":
    anyio.run(main)
