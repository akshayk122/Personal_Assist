from colorama import Fore 
from mcp.server.fastmcp import FastMCP
import json
import requests

mcp=FastMCP()

@mcp.tool()
def list_places_visited(query:str)->str:
    """This tool is used to get the list places i visited
    Args:
        days: the int number of days i want to visit the places
        example: 3

    returns:
    str:a list of places i visited
    example response: "California, New York, London"
    """
    url="https://github.com/akshayk122/ACP/blob/main/visited_places.json"
    response=requests.get(url)
    places=json.loads(response.text)
    return places

if __name__ == "__main__":
    mcp.run(transport="stdio")
