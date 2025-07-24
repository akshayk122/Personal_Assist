"""
MCP Tools for Notes Management
Simplified version with Supabase storage
"""

from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import json
import sys
import os
from collections import defaultdict

from utils.supabase_config import supabase_manager

mcp=FastMCP()

@mcp.tool()
def list_notes(
    note_id: str = 'sample-n001'
) -> str:
    """List notes from Supabase"""
    try:
        notes = supabase_manager.get_notes(note_id)
        print(notes)
        return json.dumps(notes, indent=2)
    
    except Exception as e:
        print(f"Error listing notes: {e}")  # Log the real error
        return f"Error listing notes: {str(e)}"
    
if __name__ == "__main__":
    mcp.run(transport="stdio")