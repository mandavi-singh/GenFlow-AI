import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient

from genflow.tools import LOCAL_TOOLS

SERVER_SCRIPT = str(Path(__file__).with_name("server.py"))


async def get_tools():
    client = MultiServerMCPClient(
        {"genflow-kb": {"command": sys.executable, "args": [SERVER_SCRIPT], "transport": "stdio"}}
    )
    mcp_tools = await client.get_tools()
    return LOCAL_TOOLS + mcp_tools
