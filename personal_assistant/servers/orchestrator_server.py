"""
ACP Server 3 - Personal Assistant Orchestrator 
Port: 8300

Coordinates between Meeting Manager and Expense Tracker agents
Following the pattern from acp_demo.py
"""

from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Server, RunYield, RunYieldResume
from acp_sdk.client import Client
from crewai import Agent, Task, Crew
import nest_asyncio
import sys
import os
import asyncio

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.gemini_config import get_llm

# Apply asyncio patch for Jupyter compatibility
nest_asyncio.apply()

# Initialize server and get configured LLM
server = Server()
llm = get_llm()

class SubAgentCommunicator:
    """Handles communication with meeting and expense servers"""
    
    def __init__(self):
        self.meeting_server_url = "http://localhost:8100"
        self.expense_server_url = "http://localhost:8200"
    
    async def query_meeting_agent(self, query: str) -> str:
        """Query the meeting management agent"""
        try:
            async with Client(base_url=self.meeting_server_url) as client:
                run = await client.run_sync(
                    agent="meeting_manager", 
                    input=query
                )
                return run.output[0].parts[0].content
        except Exception as e:
            return f"Unable to contact Meeting Manager: {str(e)}"
    
    async def query_expense_agent(self, query: str) -> str:
        """Query the expense tracking agent"""
        try:
            async with Client(base_url=self.expense_server_url) as client:
                run = await client.run_sync(
                    agent="expense_tracker", 
                    input=query
                )
                return run.output[0].parts[0].content
        except Exception as e:
            return f"Unable to contact Expense Tracker: {str(e)}"

# Initialize communicator
sub_agent_comm = SubAgentCommunicator()

@server.agent(name="personal_assistant")
async def orchestrator_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    try:
        # Extract user query
        user_query = input[0].parts[0].content
        query_lower = user_query.lower()
        
        # Determine which agents to query based on keywords and context
        needs_meeting_agent = any(keyword in query_lower for keyword in [
            'meeting', 'schedule', 'calendar', 'appointment', 'conflict', 
            'attendee', 'reschedule', 'cancel', 'book', 'available'
        ])
        
        needs_expense_agent = any(keyword in query_lower for keyword in [
            'expense', 'spend', 'spent', 'cost', 'money', 'budget', 'pay', 
            'paid', 'purchase', 'buy', 'bought', 'price', 'dollar', '$',
            'food', 'transportation', 'electronics', 'entertainment', 'utilities',
            'healthcare', 'shopping'
        ])
        
        # Query appropriate agents
        agent_responses = []
        
        if needs_meeting_agent:
            meeting_response = await sub_agent_comm.query_meeting_agent(user_query)
            agent_responses.append(("Meeting Manager", meeting_response))
        
        if needs_expense_agent:
            # Forward the query directly to expense agent
            expense_response = await sub_agent_comm.query_expense_agent(user_query)
            agent_responses.append(("Expense Tracker", expense_response))
            yield Message(parts=[MessagePart(content=expense_response)])
            return
        
        # If no specific agent needed, provide help
        if not agent_responses:
            help_message = """**Personal Assistant Help**

I can help you with:

1. Meeting Management:
   - "Schedule a team meeting tomorrow at 9 AM"
   - "Show my meetings for this week"
   - "Check for conflicts on Friday"

2. Expense Tracking:
   - "Show my food expenses"
   - "I spent $25 on lunch"
   - "List my transportation expenses"
   - "How much did I spend on electronics?"

3. Combined Queries:
   - "What meetings do I have and what did I spend this week?"
   - "Show my schedule and food expenses"

Available expense categories: food, transportation, electronics, entertainment, utilities, healthcare, shopping"""
            yield Message(parts=[MessagePart(content=help_message)])
            return
        
        # For multiple agent responses, combine them
        if len(agent_responses) > 1:
            response = "\n\n".join(f"## {name} Response:\n{resp}" for name, resp in agent_responses)
            response += "\n\n🔗 Integrated Summary: The above responses have been coordinated to provide comprehensive assistance."
            yield Message(parts=[MessagePart(content=response)])
            return
            
    except Exception as e:
        error_response = f"Error in Personal Assistant: {str(e)}"
        yield Message(parts=[MessagePart(content=error_response)])

if __name__ == "__main__":
    print(" Starting Personal Assistant Orchestrator on port 8300...")
    print("Available endpoints:")
    print("  - POST /runs (agent: personal_assistant)")
    print("Coordinates between:")
    print("  - Meeting Manager (port 8100)")
    print("  - Expense Tracker (port 8200)")
    print("\n Example queries:")
    print(" 'Schedule a meeting with John tomorrow at 2 PM'")
    print("'I spent $25 on lunch today'") 
    print("'What meetings do I have this week and my food expenses?'")
    
    server.run(port=8300) 