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
            role="Task Manager",
            goal="Help users manage their tasks (add, list, delete, complete)",
            backstory="You are a helpful assistant for personal task management.",
            llm=llm,
            verbose=False,
            allow_delegation=False
        )

    def handle(self, query: str) -> str:
        # Static response logic
        query_lower = query.lower()
        if "add" in query_lower:
            response = "✅ Task added: 'Finish project report by Friday'."
        elif "list" in query_lower or "show" in query_lower:
            response = (
                "📝 Your tasks:\n"
                "1. Finish project report by Friday\n"
                "2. Call Alice about the meeting\n"
                "3. Submit expense receipts"
            )
        elif "delete" in query_lower or "remove" in query_lower:
            response = (
                "🗑️ Task deleted: 'Call Alice about the meeting'.\n"
                "Remaining tasks:\n"
                "1. Finish project report by Friday\n"
                "2. Submit expense receipts"
            )
        elif "complete" in query_lower or "done" in query_lower:
            response = "🎉 Marked 'Submit expense receipts' as complete!"
        else:
            response = (
                "🤖 I can help you add, list, delete, or complete tasks.\n"
                "Try: 'add a new task', 'list my tasks', or 'delete task 2'."
            )

        # Define a CrewAI Task (for future LLM use)
        task = Task(
            description=f"Process this task-related request: '{query}'",
            expected_output="A clear, actionable response to the user's task management request.",
            agent=self.agent,
            verbose=False
        )

        # Create and run the Crew (not using LLM for now, just static)
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False
        )
        result = crew.kickoff_async()
        # For now, just return the static response
        return result