"""
Expense Tracker Server
Port: 8200

Handles expense tracking and management
"""

import logging
import os
from dotenv import load_dotenv
from collections.abc import AsyncGenerator
from datetime import datetime
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Server, RunYield, RunYieldResume
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
import nest_asyncio
import sys
import os
from dotenv import load_dotenv
from typing import Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
print(f"[Expense Server] Environment check:")
print(f"SUPABASE_URL: {'SET' if os.getenv('SUPABASE_URL') else 'MISSING'}")
print(f"SUPABASE_API_KEY: {'SET' if os.getenv('SUPABASE_API_KEY') else 'MISSING'}")

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.gemini_config import get_llm
from mcp_tools.expense_tools import (
    add_expense, list_expenses, get_expense_summary,
    update_expense, delete_expense, filter_expenses
)

# Apply asyncio patch for Jupyter compatibility
nest_asyncio.apply()

# Initialize server and get configured LLM
server = Server()
llm = get_llm()

# Create proper CrewAI tools
class AddExpenseTool(BaseTool):
    name: str = "add_expense"
    description: str = """ONLY use this tool when the user wants to add a new expense.
    Examples: 
    - "I spent $20 on lunch"
    - "Add expense: $50 for gas"
    - "Record $100 for electronics"
    DO NOT use this tool for viewing or listing expenses."""

    def _run(self, amount: float, category: str, description: str, date: str = "", payment_method: str = "credit") -> str:
        return add_expense(amount=amount, category=category, description=description, date=date, payment_method=payment_method)

class ListExpensesTool(BaseTool):
    name: str = "list_expenses"
    description: str = """ONLY use this tool for simple list/show/display expense requests.
    Examples:
    - "list my expenses"
    - "show my expenses"
    - "display expenses"
    - "what are my expenses"
    DO NOT use this tool for summaries or analytics.
    DO NOT use this tool after using other tools."""

    def _run(self, start_date: str = "", end_date: str = "", category: str = "all", list_all: bool = True) -> str:
        # For simple list requests, use list_all=True to show all expenses
        return list_expenses(start_date=start_date, end_date=end_date, category=category, list_all=list_all)

class FilterExpensesTool(BaseTool):
    name: str = "filter_expenses"
    description: str = """ONLY use this tool for category-specific expense queries.
    Examples:
    - "show food expenses"
    - "list transportation costs"
    - "what did I spend on electronics"
    DO NOT use this tool for general expense listing."""

    def _run(self, category: str) -> str:
        return filter_expenses(category=category)

class GetExpenseSummaryTool(BaseTool):
    name: str = "get_expense_summary"
    description: str = """ONLY use this tool for summary/analytics requests.
    Examples:
    - "summarize my expenses"
    - "give me a spending summary"
    - "analyze my expenses"
    DO NOT use this tool for simple expense listing.
    DO NOT use this tool unless explicitly asked for a summary."""

    def _run(self, period: str = "month", group_by: str = "category") -> str:
        return get_expense_summary(period=period, group_by=group_by)

class UpdateExpenseTool(BaseTool):
    name: str = "update_expense"
    description: str = """ONLY use this tool to modify existing expenses.
    Examples:
    - "update expense ABC123"
    - "change expense details"
    - "modify expense amount"
    DO NOT use this tool for viewing expenses."""

    def _run(self, expense_id: str, updates: str) -> str:
        return update_expense(expense_id=expense_id, updates=updates)

class DeleteExpenseTool(BaseTool):
    name: str = "delete_expense"
    description: str = """ONLY use this tool to remove expenses.
    Examples:
    - "delete expense ABC123"
    - "remove expense"
    DO NOT use this tool for viewing expenses."""

    def _run(self, expense_id: str) -> str:
        return delete_expense(expense_id=expense_id)

# Initialize tools
expense_tools = [
    AddExpenseTool(),
    ListExpensesTool(),
    FilterExpensesTool(),
    GetExpenseSummaryTool(),
    UpdateExpenseTool(),
    DeleteExpenseTool()
]

@server.agent(name="expense_tracker")
async def expense_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """This agent manages personal and business expenses using various tools"""
    
    # Create the expense management agent
    expense_manager = Agent(
        role="Expense Management Expert",
        goal="Help users track, manage, and analyze their expenses efficiently",
        backstory="""You are an expert financial assistant specializing in expense management.
        You follow these STRICT rules when choosing tools:

        1. For viewing expenses, ONLY use ONE of these tools (never both):
           - list_expenses: for simple "show/list/display expenses" requests
           - filter_expenses: for category-specific requests
           - get_expense_summary: ONLY when explicitly asked for summary/analysis
        
        2. For modifying expenses:
           - add_expense: ONLY for new expenses
           - update_expense: ONLY for modifying existing expenses
           - delete_expense: ONLY for removing expenses

        You MUST:
        - Choose exactly ONE tool based on the query type
        - Use list_expenses for any general expense viewing request
        - Never combine get_expense_summary with list_expenses
        - Never try multiple tools for the same query

        Example mappings:
        - "list expenses" → list_expenses
        - "show food expenses" → filter_expenses
        - "summarize spending" → get_expense_summary
        - "I spent $20" → add_expense""",
        llm=llm,
        tools=expense_tools,
        allow_delegation=False,
        verbose=True
    )

    # Create the task for handling the user's expense query
    task = Task(
        description=f"Choose ONE appropriate tool to handle: {input[0].parts[0].content}",
        expected_output="Direct response using exactly one tool - no combinations or retries.",
        agent=expense_manager,
        verbose=True
    )

    # Create and run the crew
    crew = Crew(
        agents=[expense_manager],
        tasks=[task],
        verbose=True
    )

    # Execute the task and get result
    result = await crew.kickoff_async()
    
    # Return the result
    yield Message(parts=[MessagePart(content=str(result))])

if __name__ == "__main__":
    print("Starting Expense Tracker Server on port 8200...")
    print("Available endpoints:")
    print("  - POST /runs (agent: expense_tracker)")
    print("\nExample queries:")
    print("  - 'Show my food expenses this month'")
    print("  - 'I spent $25 on lunch today'")
    print("  - 'List my expenses'")
    print("  - 'Show me what I spent'")
    server.run(port=8200) 