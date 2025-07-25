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

@mcp.tool()
def add_note(
    content: str,
    is_completed: bool = False
) -> str:
    """Add a new note to Supabase"""
    try:
        note_data = {
            "content": content,
            "iscompleted": is_completed
        }
        note_id = supabase_manager.add_note(note_data)
        return f"Note added with ID: {note_id}"
    except Exception as e:
        print(f"Error adding note: {e}")
        return f"Error adding note: {str(e)}"

@mcp.tool()
def update_note(
    note_id: str,
    content: str = None,
    is_completed: bool = None
) -> str:
    """Update a note's content or completion status in Supabase"""
    try:
        updates = {}
        if content is not None:
            updates["content"] = content
        if is_completed is not None:
            updates["iscompleted"] = is_completed
        if not updates:
            return "No updates provided. Specify content or is_completed."
        from utils.supabase_config import supabase_manager
        success = supabase_manager.update_note(note_id, updates)
        if success:
            return f"Note {note_id} updated successfully."
        else:
            return f"Failed to update note {note_id}."
    except Exception as e:
        print(f"Error updating note: {e}")
        return f"Error updating note: {str(e)}"
    
if __name__ == "__main__":
    mcp.run(transport="stdio")