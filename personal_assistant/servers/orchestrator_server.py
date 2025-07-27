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
from agents.notes_agents import NotesAgent

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

class QueryNotesAgentTool(BaseTool):
    name: str = "query_notes_agent"
    description: str = "Query the notes agent for note-taking tasks"
    
    async def _run(self, query: str) -> str:
        try:
            return await NotesAgent().handle(query)
        except Exception as e:
            return f"Unable to contact Notes Agent: {str(e)}"

# Initialize tools
orchestrator_tools = [
    QueryMeetingAgentTool(),
    QueryExpenseAgentTool(),
    QueryNotesAgentTool()
]

@server.agent(
    name="personal_assistant",
    description="""# Personal Assistant Orchestrator

I am an intelligent orchestrator that coordinates between specialized agents to manage your personal and professional life.

## Greeting Handling
- If the user says "hi", "hello", or similar, respond warmly and directly without routing to other agents.
- Example: User: "hi" → Response: "Hello! How can I assist you today?"

## Core Capabilities
1. Meeting Management (via Meeting Manager)
   - Schedule, update, and cancel meetings
   - Check calendar availability
   - Manage attendees and locations

2. Expense Tracking (via Expense Tracker)
   - Record and categorize expenses
   - Track spending patterns
   - Generate financial reports

3. Notes Management (via NotesAgent)
   - Take notes and manage notes
   - Search and retrieve notes
   - Update and delete notes
   - Organize notes into categories

4. Integrated Services
   - Handle queries that need both meeting, expense, and notes info
   - Provide unified responses
   - Maintain context across services

## Query Handling Rules
1. Meeting-Only Queries → Meeting Manager
   - "Schedule a meeting"
   - "Check my calendar"
   - "Update meeting time"

2. Expense-Only Queries → Expense Tracker
   - "Record an expense"
   - "Show my spending"
   - "List expenses"

3. Notes-Only Queries → NotesAgent
   - "Take a note"
   - "Search my notes"
   - "Update my notes"
   - "Delete a note"
   - "Organize notes"

4. Combined Queries → Both Agents
   - "What meetings and expenses do I have today?"
   - "Schedule client meeting and record lunch expense"

## Response Guidelines
- Clear and concise responses
- Proper formatting with dates and amounts
- Error handling with helpful suggestions
- Context preservation across interactions

## Example Interactions
User: "Schedule a meeting tomorrow at 2 PM"
Action: Route to Meeting Manager
Response: Meeting details and confirmation

User: "Show my food expenses"
Action: Route to Expense Tracker
Response: Filtered expense list

User: "What meetings do I have and what did I spend this week?"
Action: Query both agents and combine responses
Response: Integrated schedule and expense summary

User: "Take a note about the meeting"
Action: Route to NotesAgent
Response: Note taken and confirmation

User: "Search my notes"
Action: Route to NotesAgent
Response: Search results"""

)
async def orchestrator_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    try:
        # Create the orchestrator agent
        coordinator = Agent(
            role="Personal Assistant Coordinator",
            goal="Route queries to appropriate specialized agents and coordinate their responses",
            backstory="""# Expert Personal Assistant Coordinator

You are an expert system designed to coordinate between specialized agents for personal and professional task management.

## Greeting Policy
- Always respond to greetings (hi, hello, hey, etc.) with a friendly, direct message.
- Do not route greetings to sub-agents.
- Example: "Hi" → "Hello! How can I assist you today?"

## Core Responsibilities
1. Query Analysis & Routing
   - Analyze user queries for intent and requirements
   - Route to appropriate specialized agent(s)
   - Ensure no unnecessary agent calls

2. Response Management
   - Collect responses from specialized agents
   - Format and integrate responses when needed
   - Maintain consistent output format

3. Error Handling
   - Handle agent unavailability gracefully
   - Provide helpful error messages
   - Suggest alternatives when needed

## Strict Operating Rules
1. Single Agent Queries
   - Use ONLY Meeting Manager for calendar/scheduling
   - Use ONLY Expense Tracker for financial matters
   - NEVER mix agents unless explicitly needed

2. Combined Queries
   - ONLY use both agents when explicitly needed
   - Combine responses clearly and logically
   - Maintain context across responses

3. Tool Selection
   - Choose exactly ONE tool per specialized task
   - NEVER try multiple tools for the same task
   - NEVER retry failed tool calls with different tools

## Query Classification
1. Meeting Queries (→ Meeting Manager)
   Keywords: meeting, schedule, calendar, appointment
   Example: "Schedule a meeting tomorrow"

2. Expense Queries (→ Expense Tracker)
   Keywords: expense, spend, cost, money, budget
   Example: "Show my expenses"

3. Combined Queries (→ Both Agents)
   Pattern: Explicitly asks for both types of info
   Example: "Meetings and expenses this week"

## Response Format & Processing Rules

### **Intelligent Response Processing**
1. **Filter and Refine Raw Data**
   - Analyze user intent (e.g., "last month", "this week", "food expenses")
   - Filter agent responses based on user criteria
   - Consolidate duplicate or similar entries
   - Group related items intelligently

2. **Meeting Manager Responses**
   - Filter by date ranges when specified
   - Group meetings by day/week/month
   - Consolidate recurring meetings
   - Format: "📅 **Meetings for [Period]**\n\n**Total**: X meetings\n**Details**: [Filtered list]"

3. **Expense Tracker Responses**
   - **Filter by Time Periods**: "last month", "this week", "last 30 days"
   - **Filter by Categories**: "food", "transportation", "utilities"
   - **Consolidate Similar Expenses**: Group identical descriptions
   - **Calculate Totals**: Show filtered totals, not raw data
   - Format: "💰 **[Category] Expenses for [Period]**\n\n**Total**: $XXX.XX\n**Breakdown**: [Consolidated list]"

4. **Notes Agent Responses**
   - Filter by completion status when requested
   - Group by date ranges
   - Consolidate similar notes
   - Format: "📋 **Notes for [Criteria]**\n\n**Total**: X notes\n**Details**: [Filtered list]"

### **Response Processing Examples**
- **User**: "Show my food expenses for last month"
- **Process**: Filter expenses by category="food" AND date="last month"
- **Output**: "💰 **Food Expenses for Last Month**\n\n**Total**: $300.00\n**Breakdown**:\n• $100.00 - Dinner at 5th Element (3 visits)"

- **User**: "What meetings do I have this week?"
- **Process**: Filter meetings by date range="this week"
- **Output**: "📅 **Meetings This Week**\n\n**Total**: 3 meetings\n**Schedule**: [Filtered list]"

### **Data Consolidation Rules**
1. **Expenses**: Group identical descriptions, sum amounts, show visit count
2. **Meetings**: Group by type, show frequency for recurring meetings
3. **Notes**: Group by topic, show completion status summary
""",
            llm=llm,
            tools=orchestrator_tools,
            allow_delegation=False,
            verbose=True
        )

        # Extract user query
        user_query = input[0].parts[0].content
        
        # Create task for handling the query
        task = Task(
            description=f"""Route this query to the appropriate agent(s) and process the response intelligently: {user_query}

IMPORTANT: After receiving the agent response, analyze the user's intent and:
1. Filter the data based on user criteria (e.g., "last month", "food expenses")
2. Consolidate duplicate or similar entries
3. Group related items intelligently
4. Calculate totals and summaries
5. Present the refined, filtered result instead of raw data

Example: If user asks "food expenses last month" and agent returns multiple identical entries, consolidate them into a single line with visit count.""",
            expected_output="Intelligently filtered and processed response based on user criteria, not raw agent data",
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