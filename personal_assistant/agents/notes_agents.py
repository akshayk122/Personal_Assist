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

llm = get_llm()

class NotesAgent:
    def __init__(self):
        self.agent = Agent(
            role="Notes Manager",
            goal="Help users manage their notes (add, list, delete)",
            backstory="You are a helpful assistant for personal note-taking and reminders.",
            llm=llm,
            verbose=False,
            allow_delegation=False
        )

    async def handle(self, query: str) -> str:
        # Create a CrewAI Task
        task = Task(
            description=f"Process this note-related request: '{query}' and return the result with most professional and concise manner",
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