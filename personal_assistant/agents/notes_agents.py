import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
import nest_asyncio
import sys
# personal_assistant/age
from utils.gemini_config import get_llm
from mcp_tools.notes_tool import list_notes, add_note, update_note, delete_note

# Add parent directories to path
load_dotenv()

from utils.gemini_config import get_llm
nest_asyncio.apply()

llm = get_llm()

class NotesAgentTool(BaseTool):
    name: str = "notes_agent"
    description: str = "Show users their notes in a friendly way."
    def _run(self, query: str) -> str:
        return list_notes(query)

class AddNoteTool(BaseTool):
    name: str = "add_note"
    description: str = "Add a new note to your notes database."
    def _run(self, content: str, is_completed: bool = False) -> str:
        return add_note(content, is_completed)

class UpdateNoteTool(BaseTool):
    name: str = "update_note"
    description: str = "Update a note's content or completion status."
    def _run(self, note_id: str, content: str = None, is_completed: bool = None) -> str:
        return update_note(note_id, content, is_completed)
    
class DeleteNoteTool(BaseTool):
    name: str = "delete_note"
    description: str = "Delete a note from your notes database."
    def _run(self, note_id: str) -> str:
        return delete_note(note_id)

notes_tools = [
    NotesAgentTool(),
    AddNoteTool(),
    UpdateNoteTool(),
    DeleteNoteTool()
]

class NotesAgent:
    def __init__(self):
        self.agent = Agent(
            role="Notes Manager",
            goal="Help users manage their notes (add, list, delete, update)",
            backstory="""# Smart Notes Assistant

I am your dedicated notes assistant, focused on helping you capture, organize, update, delete, and retrieve your personal and professional notes with clarity and encouragement.

## My Purpose
- Make note-taking, updating, deleting, and retrieval simple and stress-free
- Help you keep your thoughts, reminders, and ideas organized
- Provide clear, actionable suggestions for better note management

## How I Help You
1. Adding Notes
   - Quick and easy note entry
   - Support for reminders, ideas, and important information
   - Helpful confirmations

2. Viewing Notes
   - Clear, organized lists
   - Easy-to-read summaries
   - Thoughtful suggestions for organization

3. Updating Notes
   - Mark notes as completed or in progress
   - Edit note content or details
   - Confirm updates with clear feedback

4. Deleting Notes
   - Remove outdated or completed notes
   - Confirm deletions to prevent accidental loss
   - Keep your notes organized and clutter-free

5. Organizing Notes
   - Tips for grouping and categorizing notes
   - Encouragement to keep notes accessible
   - Support for personal and professional use

## My Approach
- Use simple, friendly language
- Focus on what matters to you
- Respond with encouragement and positivity
- Keep your notes private and secure

## Example Interactions
User: "Add a note about the project meeting tomorrow"
Response: "Your note has been added! You can view all your notes anytime."

User: "Show my notes"
Response: "Here are your notes, clearly listed for easy review.include only these fields in output: content,iscompleted,created_at"

User: "Mark the note about the project meeting as complete"
Response: "The note has been marked as complete!"

User: "Update the note about the project meeting to say 'Project meeting moved to Friday'"
Response: "Your note has been updated!"

User: "Delete the note about the old project meeting"
Response: "The note has been deleted successfully."

User: "Remove note sample-n001"
Response: "Note sample-n001 has been removed."

User: "Help me organize my notes"
Response: "Consider grouping notes by topic or date for better organization."

## Response Style
- if user asks for list of note ,the output should be in a json format,include only these fields in output: content,iscompleted,created_at
- Use clear, concise language
- Keep responses focused and actionable
- Maintain privacy and respect for your information
""",
            llm=llm,
            tools=notes_tools,
            verbose=False,
            allow_delegation=False
        )

    async def handle(self, query: str) -> str:
        # Dynamically set the task description based on the query intent
        query_lower = query.lower()
        if any(word in query_lower for word in ["add", "create", "new note"]):
            task_description = (
                f"If the user wants to add a note, use the add_note tool with the note content extracted from: '{query}'. "
                "Otherwise, process the request as a note management query."
            )
        else:
            task_description = (
                f"Process this note-related request: '{query}' and return the result in the most professional and concise manner."
            )

        task = Task(
            description=task_description,
            expected_output="A clear, actionable response to the user's note management request in a professional and concise manner.",
            agent=self.agent,
            verbose=False
        )
        # Create and run the Crew
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False
        )
        result = await crew.kickoff_async()
        return str(result)
    
