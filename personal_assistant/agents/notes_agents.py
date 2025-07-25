import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
import nest_asyncio
import sys
import os

# Add parent directories to path
load_dotenv()

from utils.gemini_config import get_llm
nest_asyncio.apply()
llm = get_llm()

# personal_assistant/agents/task_agent.py

from crewai import Agent, Task, Crew
from utils.gemini_config import get_llm
from mcp_tools.notes_tool import list_notes, add_note
from crewai.tools import BaseTool

llm = get_llm()

class ListNotesTool(BaseTool):
    name: str = "notes_agent"
    description: str = "Show users their notes in a friendly way."
    def _run(self, query: str) -> str:
        return list_notes(query)

class AddNoteTool(BaseTool):
    name: str = "add_note"
    description: str = "Add a new note to your notes database."
    def _run(self, content: str, is_completed: bool = False) -> str:
        return add_note(content, is_completed)

notes_tools = [
    ListNotesTool(),
    AddNoteTool()
]

class NotesAgent:
    def __init__(self):
        self.agent = Agent(
            role="Notes Manager",
            goal="Help users manage their notes (add, list, delete)",
            backstory="""# Smart Notes Assistant

I am your dedicated notes assistant, focused on helping you capture, organize, and retrieve your personal and professional notes with clarity and encouragement.

## My Purpose
- Make note-taking and retrieval simple and stress-free
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

3. Organizing Notes
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
Response: "Here are your notes, clearly listed for easy review."

User: "Help me organize my notes"
Response: "Consider grouping notes by topic or date for better organization."

## Response Style
- Be warm and encouraging
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
    
