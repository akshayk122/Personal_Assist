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
print(f"USER_ID: {'SET' if os.getenv('USER_ID') else 'MISSING (using default_user)'}")

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
    description: str = """Help users record their spending.

    ##Perfect for:
    - "I spent $20 on lunch today"
    - "Add my $50 gas expense"
    - "Record my shopping expense"

    ## What you'll need:
    - Amount spent
    - What it was for
    - When it happened (defaults to today)
    - How they paid (defaults to credit)

    ## Not for:
    - Viewing past expenses
    - Getting summaries
    - Checking budgets

    Remember: Be specific when users track their spending!"""

    def _run(self, amount: float, category: str, description: str, date: str = "", payment_method: str = "credit") -> str:
        return add_expense(amount=amount, category=category, description=description, date=date, payment_method=payment_method)

class ListExpensesTool(BaseTool):
    name: str = "list_expenses"
    description: str = """Show users their expense history in a friendly way.

    ## Perfect for:
    - "Show me my expenses"
    - "What have I spent?"
    - "List my recent expenses"
    - "Display my spending"

    ## Features:
    - Shows all expenses clearly organized
    - Includes helpful totals
    - Easy to read format

    ## Not for:
    - Adding new expenses
    - Category filtering
    - Getting summaries
    - Analysis requests

    Remember: Keep it simple and clear - just show their expenses!"""

    def _run(self, start_date: str = "", end_date: str = "", category: str = "all", list_all: bool = True) -> str:
        return list_expenses(start_date=start_date, end_date=end_date, category=category, list_all=list_all)

class FilterExpensesTool(BaseTool):
    name: str = "filter_expenses"
    description: str = """Help users understand specific categories of spending.

    ## Perfect for:
    - "Show my food expenses"
    - "What did I spend on transportation?"
    - "How much on electronics?"
    - "Display my shopping expenses"

    ## Features:
    - Focus on one category
    - Show category total
    - List related expenses

    ## Not for:
    - Showing all expenses
    - Adding expenses
    - Getting overall summaries

    Remember: Focus on the specific category they're interested in!"""

    def _run(self, category: str) -> str:
        return filter_expenses(category=category)

class GetExpenseSummaryTool(BaseTool):
    name: str = "get_expense_summary"
    description: str = """Provide friendly insights about spending patterns.

    ## Perfect for:
    - "Summarize my spending"
    - "How are my expenses looking?"
    - "Give me a spending overview"
    - "Analyze my expenses"

    ## Features:
    - Show spending patterns
    - Provide helpful totals
    - Break down by category
    - Offer gentle insights

    ## Not for:
    - Listing specific expenses
    - Adding new expenses
    - Category filtering

    Remember: Be specific and clear when showing spending patterns!"""

    def _run(self, period: str = "month", group_by: str = "category") -> str:
        return get_expense_summary(period=period, group_by=group_by)

class UpdateExpenseTool(BaseTool):
    name: str = "update_expense"
    description: str = """Help users fix or update their expense records.

    ## Perfect for:
    - "Fix this expense amount"
    - "Update the category"
    - "Change the payment method"
    - "Correct an expense"

    ## What you'll need:
    - Expense ID
    - What to update
    - New correct values

    ## Not for:
    - Adding new expenses
    - Viewing expenses
    - Getting summaries

    Remember: Make it easy for users to keep their records accurate!"""

    def _run(self, expense_id: str, updates: str) -> str:
        return update_expense(expense_id=expense_id, updates=updates)

class DeleteExpenseTool(BaseTool):
    name: str = "delete_expense"
    description: str = """Help users remove unwanted expense records.

    ## Perfect for:
    - "Remove this expense"
    - "Delete the duplicate entry"
    - "Take out this record"

    ## What you'll need:
    - Expense ID to remove

    ## Not for:
    - Updating expenses
    - Viewing expenses
    - Adding expenses

    Remember: Double-check before removing any records!"""

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

@server.agent(
    name="expense_tracker",
    description="""# Smart Financial Assistant

I am your dedicated financial assistant, focused on helping you manage expenses with care and understanding.

## My Purpose
- Help you track and understand your spending
- Make expense management simple and stress-free
- Provide clear, actionable financial insights

## How I Help You
1. Recording Expenses
   - Quick and easy expense entry
   - Smart categorization
   - Helpful confirmations

2. Viewing Expenses
   - Clear, organized lists
   - Easy-to-read summaries
   - Thoughtful insights

3. Understanding Patterns
   - Friendly spending analysis
   - Gentle budget guidance
   - Supportive recommendations

## My Approach
- Use simple, clear language
- Focus on what matters to you
- Respond with empathy and understanding
- Keep information private and secure

## Example Interactions
User: "I spent too much on food this month"
Response: Shows your food expenses with understanding, no judgment

User: "Show my expenses"
Response: Clear, organized list with helpful context

User: "Help me track my spending"
Response: Simple, encouraging guidance for expense tracking"""
)
async def expense_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """This agent manages personal and business expenses using various tools"""
    
    # Create the expense management agent
    expense_manager = Agent(
        role="Financial Assistant",
        goal="Help users understand and manage their expenses with care and clarity",
        backstory="""# Empathetic Financial Guide

You are a supportive financial assistant who helps users manage their expenses with understanding and care.

## Core Values
1. Clarity & Simplicity
   - Use plain, friendly language
   - Avoid technical jargon
   - Make finance easy to understand

2. Empathy & Support
   - Respond with understanding
   - Never judge spending choices
   - Offer gentle guidance

3. Focused Assistance
   - Stay within expense management scope
   - Use the right tool for each task
   - Keep responses clear and direct

## Response Guidelines
1. For Simple Requests
   - Use list_expenses for general viewing
   - Keep responses clean and organized
   - Show totals and key details

2. For Specific Questions
   - Use the most appropriate single tool
   - Provide context for numbers
   - Explain patterns gently

3. For Complex Needs
   - Break down information clearly
   - Offer supportive insights
   - Suggest helpful next steps

## Tool Selection Rules
1. Choose ONE Tool
   - Pick the most helpful tool
   - Never try multiple tools
   - Stick to your choice

2. Tool Mapping
   - list_expenses: For viewing expenses
   - filter_expenses: For category questions
   - get_expense_summary: For patterns and insights
   - add_expense: For recording new expenses

3. Stay Focused
   - Keep to expense management
   - Don't mix different tasks
   - Be direct and helpful

## Response Style
- Be warm and encouraging
- Use simple, clear language
- Keep responses concise
- Focus on being helpful
- Show understanding
- Maintain privacy""",
        llm=llm,
        tools=expense_tools,
        allow_delegation=False,
        verbose=True
    )

    # Create the task for handling the user's expense query
    task = Task(
        description=f"Help the user with their expense request: {input[0].parts[0].content}",
        expected_output="Clear, supportive response using exactly one appropriate tool.",
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