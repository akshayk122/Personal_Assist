from colorama import Fore 
from mcp.server.fastmcp import FastMCP
import json
import requests

mcp = FastMCP("places-server")

@mcp.tool()
def list_places_visited(state: str) -> list[str]:
    """Returns a list of places I visited in the given state"""
    visits = {
        "CA": ["San Francisco", "Los Angeles", "Yosemite"],
        "NY": ["New York City", "Buffalo", "Niagara Falls"],
        "TX": ["Austin", "Dallas", "Houston"],
        "IL": ["Chicago", "Springfield"],
    }

    state = state.strip().upper()
    print(f"🔍 MCP tool called with state: {state}")
    result = visits.get(state, [f"No visits logged for {state}"])
    print(f"📤 Returning response: {result}")
    return result


if __name__ == "__main__":
    print("🚀 Starting MCP server...")
    mcp.run(transport="stdio")