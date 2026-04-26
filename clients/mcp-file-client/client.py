import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_server(self, server_script_path: str):
        if server_script_path == None:
            raise ValueError("Must provide script path")
        
        is_python = server_script_path.endswith(".py")
        is_js = server_script_path.endswith(".js")

        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
        
        command = "python3" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.read, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.read, self.write))

        await self.session.initialize()

        response = await self.session.list_tools()
        print(response)

    async def cleanup(self):
        await self.exit_stack.aclose()

async def process_query(query, client):
    """Process a query using Claude and available tools"""
    anthropic = Anthropic()

    messages = [
        {
            "role": "user",
            "content": query
        }
    ]

    tool_response = await client.session.list_tools()

    available_tools = [{
            "name":tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema
        }
        for tool in tool_response.tools]
    
    response = anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=messages,
        tools=available_tools
    )

    final_response = []

    for content in response.content:
        if content.type == "text":
            final_response.append(content.text)

        elif content.type == "tool_use":
            tool_name = content.name
            tool_args = content.input

            final_response.append(f"[Calling tool {tool_name} with args {tool_args}]")
            result = await client.session.call_tool(tool_name, tool_args)
            
            messages.append({
                "role": "assistant",
                "content": content
            })

            messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": content.id,
                        "content": result.content
                    }
                ]
            })

            response = anthropic.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=messages,
                tools=available_tools
            )

            final_response.append(response.content[0].text)

    return "\n".join(final_response)


async def chat_loop(client):
    """Run interactive chat loop"""
    print("\nMCP Client Started!")
    print("Type your queries or 'quit' to exit.")

    while True:
        try:
            query = input("\nquery: ").strip()

            if query.lower() == "quit":
                break

            response = await process_query(query, client)

            print("\n" + response)

        except Exception as e:
            print(f"\nError: {str(e)}")


async def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: uv run client.py <path-to-server-script>")
        sys.exit(1)

    client = MCPClient()

    try:
        await client.connect_to_server(sys.argv[1])
        await chat_loop(client)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())


