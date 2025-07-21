"""
ACP Server 3 - Personal Assistant Orchestrator 
Port: 8300

Coordinates between Meeting Manager and Expense Tracker agents
Following the pattern from acp_demo.py
"""

import logging
import os
from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Server, RunYield, RunYieldResume
from acp_sdk.client import Client
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
import nest_asyncio
import sys
import os
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.gemini_config import get_llm

# Apply asyncio patch for Jupyter compatibility
nest_asyncio.apply()

# Initialize server and get configured LLM
server = Server()
llm = get_llm()

# Create CrewAI tools for sub-agent communication
class QueryMeetingAgentTool(BaseTool):
    name: str = "query_meeting_agent"
    description: str = "Query the meeting management agent for scheduling and calendar related tasks"
    
    async def _run(self, query: str) -> str:
        try:
            async with Client(base_url="http://localhost:8100") as client:
                run = await client.run_sync(
                    agent="meeting_manager", 
                    input=query
                )
                return run.output[0].parts[0].content
        except Exception as e:
            return f"Unable to contact Meeting Manager: {str(e)}"

class QueryExpenseAgentTool(BaseTool):
    name: str = "query_expense_agent"
    description: str = "Query the expense tracking agent for financial management tasks"
    
    async def _run(self, query: str) -> str:
        try:
            async with Client(base_url="http://localhost:8200") as client:
                run = await client.run_sync(
                    agent="expense_tracker", 
                    input=query
                )
                return run.output[0].parts[0].content
        except Exception as e:
            return f"Unable to contact Expense Tracker: {str(e)}"

# Initialize tools
orchestrator_tools = [
    QueryMeetingAgentTool(),
    QueryExpenseAgentTool()
]

@server.agent(
    name="personal_assistant",
    description="""I am your Personal Assistant Orchestrator, coordinating between specialized agents to help manage your schedule and finances.

Capabilities:
1. Route queries to appropriate specialized agents:
   - Meeting Manager for calendar and scheduling (meetings, appointments, schedule)
   - Expense Tracker for financial management (expenses, spending, money, costs)
2. Handle combined queries that need multiple agents
3. Provide integrated responses

Example queries:
- "Schedule a meeting tomorrow at 2 PM" → Meeting Manager
- "Show my food expenses this month" → Expense Tracker
- "What meetings do I have and what did I spend this week?" → Both agents

I ensure seamless coordination between different aspects of your personal and professional life."""
)
async def orchestrator_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    try:
        # Create the orchestrator agent
        coordinator = Agent(
            role="Personal Assistant Coordinator",
            goal="Route queries to the appropriate specialized agent and coordinate responses",
            backstory="""You are an expert personal assistant coordinator who routes queries to specialized agents.
            
            You follow these strict rules for routing:
            1. Meeting-related keywords (ONLY use Meeting Manager):
               - meeting, schedule, appointment, calendar, availability
               - book, reschedule, cancel (when about meetings)
               - conflict, attendee, room, zoom
            
            2. Expense-related keywords (ONLY use Expense Tracker):
               - expense, spend, spent, cost, money, budget
               - pay, paid, purchase, buy, bought
               - price, dollar, $, bill
               - food, transportation, electronics (when about spending)
            
            3. Combined queries (Use BOTH agents):
               - Only when the query explicitly asks about both meetings AND expenses
               - Example: "What meetings do I have and what did I spend this week?"
            
            You NEVER:
            - Try multiple agents unless explicitly needed for combined queries
            - Use Meeting Manager for expense queries or vice versa
            - Make multiple attempts with the same agent""",
            llm=llm,
            tools=orchestrator_tools,
            allow_delegation=False,
            verbose=True
        )

        # Extract user query
        user_query = input[0].parts[0].content
        
        # Create task for handling the query
        task = Task(
            description=f"Route this query to the appropriate agent(s): {user_query}",
            expected_output="Direct response from the appropriate specialized agent(s) without multiple attempts",
            agent=coordinator,
            verbose=True
        )

        # Create and run the crew
        crew = Crew(
            agents=[coordinator],
            tasks=[task],
            verbose=True
        )

        # Execute the task and get result
        result = await crew.kickoff_async()
        
        # Return the result
        yield Message(parts=[MessagePart(content=str(result))])
            
    except Exception as e:
        error_response = f"Error in Personal Assistant: {str(e)}"
        yield Message(parts=[MessagePart(content=error_response)])

if __name__ == "__main__":
    print("Starting Personal Assistant Orchestrator on port 8300...")
    print("Available endpoints:")
    print("  - POST /runs (agent: personal_assistant)")
    print("Coordinates between:")
    print("  - Meeting Manager (port 8100)")
    print("  - Expense Tracker (port 8200)")
    print("\nExample queries:")
    print("  - 'Schedule a meeting with John tomorrow at 2 PM'")
    print("  - 'I spent $25 on lunch today'")
    print("  - 'What meetings do I have this week and my food expenses?'")
    
    server.run(port=8300) 