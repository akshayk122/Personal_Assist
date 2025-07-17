"""
MCP Tools for Meeting Management
Following the pattern from the existing MCP server setup
"""

from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.data_manager import DataManager

# Initialize MCP server
mcp = FastMCP()
data_manager = DataManager()

@mcp.tool()
def add_meeting(
    title: str,
    date: str,
    time: str,
    duration_minutes: int = 60,
    attendees: str = "",
    location: str = "",
    description: str = ""
) -> str:
    """Add a new meeting to the calendar
    
    Args:
        title: Meeting title/subject
        date: Meeting date in YYYY-MM-DD format
        time: Meeting time in HH:MM format
        duration_minutes: Duration of meeting in minutes (default: 60)
        attendees: Comma-separated list of attendee emails
        location: Meeting location (physical or virtual)
        description: Meeting description or agenda
    
    Returns:
        str: Success message with meeting ID
    
    Example:
        add_meeting("Team Standup", "2024-01-20", "09:00", 30, "john@company.com,sarah@company.com", "Conference Room A", "Daily sync")
    """
    try:
        # Parse attendees
        attendee_list = [email.strip() for email in attendees.split(",") if email.strip()]
        
        meeting_data = {
            "title": title,
            "date": date,
            "time": time,
            "duration_minutes": duration_minutes,
            "attendees": attendee_list,
            "location": location,
            "description": description,
            "status": "scheduled"
        }
        
        meeting_id = data_manager.add_meeting(meeting_data)
        return f"Meeting '{title}' scheduled successfully with ID: {meeting_id}"
        
    except Exception as e:
        return f"Error adding meeting: {str(e)}"

@mcp.tool()
def list_meetings(
    start_date: str = "",
    end_date: str = "",
    status: str = "all"
) -> str:
    """List meetings within a date range
    
    Args:
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        status: Filter by status: scheduled|completed|cancelled|all (default: all)
    
    Returns:
        str: Formatted list of meetings
    
    Example:
        list_meetings("2024-01-15", "2024-01-20", "scheduled")
    """
    try:
        meetings = data_manager.get_meetings()
        
        # Filter by date range if provided
        if start_date:
            meetings = [m for m in meetings if m["date"] >= start_date]
        if end_date:
            meetings = [m for m in meetings if m["date"] <= end_date]
        
        # Filter by status if not "all"
        if status != "all":
            meetings = [m for m in meetings if m["status"] == status]
        
        if not meetings:
            return "📅 No meetings found for the specified criteria."
        
        # Format meetings list
        result = f"📅 Found {len(meetings)} meeting(s):\n\n"
        for meeting in meetings:
            attendees_str = ", ".join(meeting.get("attendees", []))
            result += f"🕐 **{meeting['title']}**\n"
            result += f"   📅 {meeting['date']} at {meeting['time']} ({meeting['duration_minutes']} min)\n"
            result += f"   📍 {meeting['location']}\n"
            result += f"   👥 Attendees: {attendees_str}\n"
            result += f"   📝 {meeting['description']}\n"
            result += f"   🏷️ Status: {meeting['status']}\n"
            result += f"   🆔 ID: {meeting['meeting_id']}\n\n"
        
        return result
        
    except Exception as e:
        return f" Error listing meetings: {str(e)}"

@mcp.tool()
def search_meetings(query: str, search_type: str = "title") -> str:
    """Search meetings by title, attendee, or description
    
    Args:
        query: Search term
        search_type: Search field: title|attendee|description|all (default: title)
    
    Returns:
        str: Formatted list of matching meetings
    
    Example:
        search_meetings("standup", "title")
    """
    try:
        meetings = data_manager.get_meetings()
        matching_meetings = []
        
        query = query.lower()
        
        for meeting in meetings:
            match = False
            
            if search_type in ["title", "all"]:
                if query in meeting["title"].lower():
                    match = True
            
            if search_type in ["attendee", "all"]:
                for attendee in meeting.get("attendees", []):
                    if query in attendee.lower():
                        match = True
                        break
            
            if search_type in ["description", "all"]:
                if query in meeting.get("description", "").lower():
                    match = True
            
            if match:
                matching_meetings.append(meeting)
        
        if not matching_meetings:
            return f"🔍 No meetings found matching '{query}' in {search_type}."
        
        # Format results
        result = f"🔍 Found {len(matching_meetings)} meeting(s) matching '{query}':\n\n"
        for meeting in matching_meetings:
            result += f"🕐 **{meeting['title']}** on {meeting['date']} at {meeting['time']}\n"
            result += f"   📍 {meeting['location']} | 🆔 {meeting['meeting_id']}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error searching meetings: {str(e)}"

@mcp.tool()
def update_meeting(meeting_id: str, updates: str) -> str:
    """Update a meeting's details
    
    Args:
        meeting_id: The meeting ID to update
        updates: JSON string with updates (e.g., '{"title": "New Title", "time": "10:00"}')
    
    Returns:
        str: Success or error message
    
    Example:
        update_meeting("m001", '{"title": "Updated Standup", "time": "10:00"}')
    """
    try:
        # Parse updates JSON
        update_data = json.loads(updates)
        
        success = data_manager.update_meeting(meeting_id, update_data)
        
        if success:
            return f"✅ Meeting {meeting_id} updated successfully."
        else:
            return f"❌ Meeting {meeting_id} not found."
            
    except json.JSONDecodeError:
        return "❌ Invalid JSON format for updates."
    except Exception as e:
        return f"❌ Error updating meeting: {str(e)}"

@mcp.tool()
def delete_meeting(meeting_id: str) -> str:
    """Delete/cancel a meeting
    
    Args:
        meeting_id: The meeting ID to delete
    
    Returns:
        str: Success or error message
    
    Example:
        delete_meeting("m001")
    """
    try:
        success = data_manager.delete_meeting(meeting_id)
        
        if success:
            return f"✅ Meeting {meeting_id} deleted successfully."
        else:
            return f"❌ Meeting {meeting_id} not found."
            
    except Exception as e:
        return f"❌ Error deleting meeting: {str(e)}"

@mcp.tool()
def get_meeting_conflicts(date: str, time: str, duration_minutes: int = 60) -> str:
    """Check for meeting conflicts at a specific time
    
    Args:
        date: Meeting date in YYYY-MM-DD format
        time: Meeting time in HH:MM format
        duration_minutes: Duration to check for conflicts (default: 60)
    
    Returns:
        str: List of conflicting meetings or confirmation of no conflicts
    
    Example:
        get_meeting_conflicts("2024-01-15", "09:00", 30)
    """
    try:
        meetings = data_manager.get_meetings()
        
        # Parse proposed meeting time
        proposed_start = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        proposed_end = proposed_start + timedelta(minutes=duration_minutes)
        
        conflicts = []
        
        for meeting in meetings:
            if meeting["date"] == date and meeting["status"] == "scheduled":
                existing_start = datetime.strptime(f"{meeting['date']} {meeting['time']}", "%Y-%m-%d %H:%M")
                existing_end = existing_start + timedelta(minutes=meeting["duration_minutes"])
                
                # Check for overlap
                if (proposed_start < existing_end and proposed_end > existing_start):
                    conflicts.append(meeting)
        
        if not conflicts:
            return f"✅ No conflicts found for {date} at {time}."
        
        result = f"⚠️ Found {len(conflicts)} conflict(s) for {date} at {time}:\n\n"
        for conflict in conflicts:
            result += f"🕐 **{conflict['title']}**\n"
            result += f"   📅 {conflict['date']} {conflict['time']} - {conflict['duration_minutes']} min\n"
            result += f"   📍 {conflict['location']}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error checking conflicts: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio") 