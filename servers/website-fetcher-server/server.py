import anyio
import click

from mcp import types
from mcp.server import Server

from tools.fetch import fetch
from tools.extract_text import extract_text

app = Server('website-fetcher')

@app.list_tools()
async def list_tools() -> list[types.Tool]:

    return [
        types.Tool(
            name="fetch",
            description="Fetch raw html from a website",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Website URL"
                    }
                },
                "required": ["url"]
            }
        ),

        types.Tool(
            name="extract_text",
            description="Extract readable text from website",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Website url"
                    }
                },
                "required": ["url"]
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, args: dict):
    if name == "fetch":
        return await fetch(args["url"])
    
    elif name == "extract_text":
        return await extract_text(args["url"])
    
    raise ValueError("Unknown tool")

@click.command()
@click.option("--port", default=8000, help="Port to listen on for http")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "streamable-http"]),
    default="stdio",
    help="Transport Type"
)
def main(port: int, transport: str) -> int:

    if transport=="streamable-http":
        import uvicorn

        uvicorn.run(app.streamable_http_app(),
                    host="127.0.0.1",
                    port=port)

    else:
        from mcp.server.stdio import stdio_server

        async def run_stdio():
            async with stdio_server() as streams:
                
                await app.run(streams[0], streams[1], app.create_initialization_options())

        anyio.run(run_stdio)

    return 0

if __name__ == "__main__":
    main()

