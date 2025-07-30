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
from agents.health_diet_agent import HealthDietAgent

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
        
class QueryHealthDietAgentTool(BaseTool):
    name: str = "query_health_diet_agent"
    description: str = "Query the health and diet agent for health and diet related tasks"
    
    async def _run(self, query: str) -> str:
        return await HealthDietAgent().handle(query)

# Initialize tools
orchestrator_tools = [
    QueryMeetingAgentTool(),
    QueryExpenseAgentTool(),
    QueryNotesAgentTool(),
    QueryHealthDietAgentTool()
]

@server.agent(
    name="personal_assistant",
    description="""# Personal Assistant Orchestrator

Coordinates between Meeting Manager, Expense Tracker, and Notes agents to provide intelligent responses.

## Core Capabilities
- **Meeting Management**: Schedule, update, cancel meetings
- **Expense Tracking**: Record, categorize, analyze expenses  
- **Notes Management**: Create, search, organize notes
- **Integrated Services**: Handle multi-agent queries

## Query Routing
- **Meeting queries** → Meeting Manager (meeting, schedule, calendar)
- **Expense queries** → Expense Tracker (expense, spend, money, budget)
- **Notes queries** → Notes Agent (note, search, organize)
- **Health and Diet queries** → Health and Diet Agent (health, diet, fitness, nutrition, weight, exercise, meal, calorie, workout, food, goal, ate, eat, target, daily)
- **Combined queries** → Multiple agents as needed

## Response Processing Rules
- Filter data based on user criteria (time periods, categories, status)
- Consolidate duplicate entries and group related items
- Provide formatted summaries with totals and breakdowns
- Present refined results instead of raw data"""

)
async def orchestrator_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    try:
        # Create the orchestrator agent
        coordinator = Agent(
            role="Personal Assistant Coordinator",
            goal="Route queries to appropriate specialized agents and coordinate their responses",
            backstory="""# Expert Personal Assistant Coordinator

Coordinates between specialized agents for personal and professional task management.

## Core Responsibilities
- Analyze user queries and route to appropriate agents
- Process and refine agent responses based on user intent
- Handle errors gracefully and provide helpful alternatives

## Operating Rules
- Use single agent for specific queries (meeting → Meeting Manager, expense → Expense Tracker)
- Use multiple agents only when explicitly needed
- Choose exactly ONE tool per task, never retry with different tools

## Query Classification
- **Meeting queries**: meeting, schedule, calendar, appointment
- **Expense queries**: expense, spend, cost, money, budget  
- **Notes queries**: note, search, organize, complete
- **Health and Diet queries**: health, diet, fitness, nutrition, weight, exercise, meal, calorie, workout, food, goal, ate, eat, target
- **Combined queries**: Explicitly asks for multiple types of info

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
   - Format: "**Meetings for [Period]**\n\n**Total**: X meetings\n**Details**: [Filtered list]"

3. **Expense Tracker Responses**
   - **Filter by Time Periods**: "last month", "this week", "last 30 days"
   - **Filter by Categories**: "food", "transportation", "utilities"
   - **Consolidate Similar Expenses**: Group identical descriptions
   - **Calculate Totals**: Show filtered totals, not raw data
   - Format: "**[Category] Expenses for [Period]**\n\n**Total**: $XXX.XX\n**Breakdown**: [Consolidated list]"

4. **Notes Agent Responses**
   - **Filter by Status**: "completed notes", "pending notes", "all notes"
   - **Filter by Date Ranges**: "notes from last week", "today's notes", "this month"
   - **Filter by Content**: "meeting notes", "project notes", "personal notes"
   - **Consolidate Similar Notes**: Group notes by topic or category
   - **Show Completion Summary**: Count of completed vs pending notes
   - Format: "[Type] Notes for [Period]**\n\n**Total**: X notes (✓ Y completed, ⏳ Z pending)\n**Details**: [Filtered and grouped list]"

5. **Health and Diet Agent Responses**
   - **Filter by Health Goals**: "weight", "calories", "fitness", "nutrition"
   - **Filter by Food Logging**: "meals", "calories", "food items", "ate", "eat"
   - **Filter by Date Ranges**: "today", "yesterday", "this week"
   - **Filter by Goals**: "weight goals", "calorie goals", "health targets"
   - **Consolidate Food Logs**: Group meals by type and show daily totals
   - **Show Goal Progress**: Track current vs target values
   - Format: "[Type] Health/Diet Summary**\n\n**Goals**: [Current status]\n**Food Log**: [Today's meals]\n**Totals**: [Daily calories]"

### **Response Processing Examples**
- **User**: "Show my food expenses for last month"
- **Process**: Filter expenses by category="food" AND date="last month"
- **Output**: "Food Expenses for Last Month**\n\n**Total**: $300.00\n**Breakdown**:\n• $100.00 - Dinner at 5th Element (3 visits)"

- **User**: "What meetings do I have this week?"
- **Process**: Filter meetings by date range="this week"
- **Output**: "**Meetings This Week**\n\n**Total**: 3 meetings\n**Schedule**: [Filtered list]"

- **User**: "Show my completed notes from last week"
- **Process**: Filter notes by status="completed" AND date="last week"
- **Output**: "**Completed Notes from Last Week**\n\n**Total**: 5 notes (✓ 5 completed, ⏳ 0 pending)\n**Details**:\n• Meeting notes (3 notes)\n• Project tasks (2 notes)"

- **User**: "List all my meeting notes"
- **Process**: Filter notes by content containing "meeting"
- **Output**: "**Meeting Notes**\n\n**Total**: 8 notes (✓ 6 completed, ⏳ 2 pending)\n**Details**:\n• Team standup notes (4 notes)\n• Client meeting notes (3 notes)\n• Project review notes (1 note)"

- **User**: "Show my weight progress this month"
- **Process**: Filter health records by type="weight" AND date="this month"
- **Output**: "**Weight Progress This Month**\n\n**Progress**: Down 2.5 lbs (trending downward)\n**Current**: 175 lbs\n**Goal**: 170 lbs (5 lbs remaining)\n**Details**:\n• Weekly average: 175.2 lbs\n• Best day: 174.8 lbs\n• Trend: Consistent downward progress"

- **User**: "Add a weight goal of 170 lbs"
- **Process**: Create new health goal for weight
- **Output**: "Health goal added!\n\nGoal: Weight\nTarget: 170 lbs\nGoal ID: [generated_id]"

- **User**: "Add a weight goal of 170 lbs with daily calorie goal of 2000"
- **Process**: Create new health goal for weight and daily calorie goal
- **Output**: "Health goal added!\n\nGoal: Weight\nTarget: 170 lbs\nGoal ID: [generated_id]\n\nDaily Calorie Goal: 2000 calories\nCalorie Goal ID: [generated_id]"

- **User**: "What did I eat today?"
- **Process**: Filter diet records by date="today"
- **Output**: "Today's Food Log\n\nBreakfast:\n• Oatmeal with berries (320 cal)\nLunch:\n• Grilled chicken salad (450 cal)\nDinner:\n• Salmon with vegetables (680 cal)\nDaily Total: 1,450 calories\n\nDaily Calorie Goal: 2000 calories\nProgress: 72.5%\nRemaining: 550 calories"

### **Data Consolidation Rules**
1. **Expenses**: Group identical descriptions, sum amounts, show visit count
2. **Meetings**: Group by type, show frequency for recurring meetings
3. **Notes**: 
   - Group by topic/category (meeting notes, project notes, personal notes)
   - Show completion status summary (completed vs pending)
   - Consolidate similar content under common themes
   - Filter by date ranges when specified
   - Count notes by type and status
4. **Health Goals**:
   - Track goal type, target value, and current value
   - Show progress towards health goals
   - Update current values when new data is added
   - Filter by goal type (weight, calories, fitness)
   - Include daily calorie goals for food tracking
5. **Food Logs**:
   - Group by meal type (breakfast, lunch, dinner, snacks)
   - Calculate daily calorie totals
   - Show meal breakdowns with individual items
   - Track daily food intake patterns
   - Compare against daily calorie goals
   - Show progress and remaining calories
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
1. Filter the data based on user criteria (e.g., "last month", "food expenses", "completed notes", "weight goals", "today's meals")
2. Consolidate duplicate or similar entries
3. Group related items intelligently
4. Calculate totals and summaries
5. Present the refined, filtered result instead of raw data

Examples:
- If user asks "food expenses last month" and agent returns multiple identical entries, consolidate them into a single line with visit count
- If user asks "meeting notes" and agent returns all notes, filter to only show notes containing "meeting" and group by meeting type
- If user asks "completed notes from last week", filter by completion status and date range, then group by topic
- If user asks "add a weight goal of 170 lbs", create a new health goal for weight tracking
- If user asks "add a weight goal of 170 lbs with daily calorie goal of 2000", create both weight and daily calorie goals
- If user asks "what did I eat today", show today's food log grouped by meal type with daily calorie total and progress against daily calorie goal
- If user asks "log my lunch: chicken salad, 450 calories", add the food item and show updated daily totals with progress against daily calorie goal""",
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
    print("Personal Assistant Orchestrator is running on port 8300...")
    print("Available endpoints(ACP Server 3):")
    print("  - POST /runs (agent: personal_assistant)")
    print("Coordinates between:")
    print("  - Meeting Manager (port 8100)")
    print("  - Expense Tracker (port 8200)")
    print("  - Notes Agent (local)")
    print("  - Health & Diet Agent (local)")
    print("\nExample queries:")
    print("  - 'Schedule a meeting with John tomorrow at 2 PM'")
    print("  - 'I spent $25 on lunch today'")
    print("  - 'Add a note about the project meeting'")
    print("  - 'Add a weight goal of 170 lbs'")
    print("  - 'Add a weight goal of 170 lbs with daily calorie goal of 2000'")
    print("  - 'I ate oatmeal for breakfast, 320 calories'")
    print("  - 'What did I eat today?'")
    print("  - 'Update my weight goal to 165 lbs'")
    
    server.run(port=8300) 