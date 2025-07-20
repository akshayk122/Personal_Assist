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
import logging
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
    update_expense, delete_expense, get_budget_status,
    filter_expenses
)

# Apply asyncio patch for Jupyter compatibility
nest_asyncio.apply()

# Initialize server and get configured LLM
server = Server()
llm = get_llm()

# Create proper CrewAI tools
class AddExpenseTool(BaseTool):
    name: str = "add_expense"
    description: str = "Add a new expense with amount, category, description, date, and payment method"

    def _run(self, amount: float, category: str, description: str, date: str = "", payment_method: str = "credit") -> str:
        return add_expense(amount=amount, category=category, description=description, date=date, payment_method=payment_method)

class ListExpensesTool(BaseTool):
    name: str = "list_expenses"
    description: str = "List all expenses with optional filters for date range and category"

    def _run(self, start_date: str = "", end_date: str = "", category: str = "all") -> str:
        return list_expenses(start_date=start_date, end_date=end_date, category=category)

class FilterExpensesTool(BaseTool):
    name: str = "filter_expenses"
    description: str = "Filter expenses by specific category"

    def _run(self, category: str) -> str:
        return filter_expenses(category=category)

class GetExpenseSummaryTool(BaseTool):
    name: str = "get_expense_summary"
    description: str = "Get summary statistics and analytics for expenses"

    def _run(self, period: str = "month", group_by: str = "category") -> str:
        return get_expense_summary(period=period, group_by=group_by)

class UpdateExpenseTool(BaseTool):
    name: str = "update_expense"
    description: str = "Update an existing expense's details"

    def _run(self, expense_id: str, updates: str) -> str:
        return update_expense(expense_id=expense_id, updates=updates)

class DeleteExpenseTool(BaseTool):
    name: str = "delete_expense"
    description: str = "Delete an expense by ID"

    def _run(self, expense_id: str) -> str:
        return delete_expense(expense_id=expense_id)

class GetBudgetStatusTool(BaseTool):
    name: str = "get_budget_status"
    description: str = "Get budget status and spending analysis"

    def _run(self, category: str = "all", period: str = "month") -> str:
        return get_budget_status(category=category, period=period)

# Initialize tools
expense_tools = [
    AddExpenseTool(),
    ListExpensesTool(),
    FilterExpensesTool(),
    GetExpenseSummaryTool(),
    UpdateExpenseTool(),
    DeleteExpenseTool(),
    GetBudgetStatusTool()
]

@server.agent(name="expense_tracker")
async def expense_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """This agent manages personal and business expenses using various tools"""
    
    # Create the expense management agent
    expense_manager = Agent(
        role="Expense Management Expert",
        goal="Help users track, manage, and analyze their expenses efficiently",
        backstory="""You are an expert financial assistant specializing in expense management.
        You understand various expense categories, can process natural language queries about spending,
        and provide detailed financial insights. You're skilled at categorizing expenses, tracking spending patterns,
        and helping users maintain their budget.""",
        llm=llm,
        tools=expense_tools,
        allow_delegation=False,
        verbose=True
    )

    # Create the task for handling the user's expense query
    task = Task(
        description=f"Process the user's expense-related query: {input[0].parts[0].content}",
        expected_output="Clear and concise response to the user's expense query with relevant financial information.",
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
    print("  - 'What's my total spending in electronics?'")
    server.run(port=8200) 