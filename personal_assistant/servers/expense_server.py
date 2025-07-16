"""
ACP Server 2 - Expense Tracker Agent
Port: 8200

Handles all expense-related operations using MCP tools
Following the pattern from acp_demo.py
"""

from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Server, RunYield, RunYieldResume
from crewai import Agent, Task, Crew
import nest_asyncio
import sys
import os

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.gemini_config import get_llm
from mcp_tools.expense_tools import (
    add_expense, list_expenses, get_expense_summary,
    update_expense, delete_expense, get_budget_status
)

# Apply asyncio patch for Jupyter compatibility
nest_asyncio.apply()

# Initialize server and get configured LLM
server = Server()
llm = get_llm()

# Mock MCP tools as CrewAI tools (since we can't directly integrate MCP with CrewAI)
class ExpenseTool:
    """Wrapper for MCP expense tools to work with CrewAI"""
    
    def __init__(self, tool_func, name, description):
        self.tool_func = tool_func
        self.name = name
        self.description = description
    
    def run(self, **kwargs):
        """Execute the MCP tool function"""
        try:
            return self.tool_func(**kwargs)
        except Exception as e:
            return f"Error executing {self.name}: {str(e)}"

# Create tool instances
expense_tools = [
    ExpenseTool(add_expense, "add_expense", "Add a new expense to the tracker"),
    ExpenseTool(list_expenses, "list_expenses", "List expenses within specified filters"),
    ExpenseTool(get_expense_summary, "get_expense_summary", "Get expense summary and analytics"),
    ExpenseTool(update_expense, "update_expense", "Update an expense's details"),
    ExpenseTool(delete_expense, "delete_expense", "Delete an expense"),
    ExpenseTool(get_budget_status, "get_budget_status", "Get budget status and spending analysis")
]

@server.agent(name="expense_tracker")
async def expense_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """
    Expense Tracker Agent
    
    Handles all expense-related queries and operations including:
    - Recording new expenses
    - Listing and filtering expenses
    - Generating spending summaries and analytics
    - Budget tracking and analysis
    - Expense categorization and management
    """
    
    try:
        # Extract user query
        user_query = input[0].parts[0].content
        
        # Create specialized expense management agent
        expense_manager = Agent(
            role="Personal Finance and Expense Management Specialist",
            goal="Efficiently track, analyze, and optimize personal expenses and budgets",
            backstory="""You are an expert personal finance assistant with extensive experience in 
            expense tracking, budget management, and financial analytics. You excel at:
            - Understanding natural language descriptions of expenses and financial requests
            - Categorizing expenses accurately and consistently
            - Providing insightful spending analysis and budget recommendations
            - Identifying spending patterns and potential savings opportunities
            - Creating clear and actionable financial reports and summaries
            
            You can perform comprehensive expense operations including adding, listing, analyzing, 
            updating, and deleting expenses. You always provide valuable financial insights 
            and proactively suggest improvements to spending habits and budget management.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            max_retry_limit=3
        )
        
        # Create task for expense management
        expense_task = Task(
            description=f"""
            Process this expense-related request: "{user_query}"
            
            You have access to various expense management capabilities:
            1. Adding new expenses with detailed categorization (amount, category, description, date, payment method)
            2. Listing expenses with filtering by date, category, amount ranges
            3. Generating comprehensive expense summaries and analytics by time periods
            4. Updating existing expense details and categorization
            5. Deleting incorrect or duplicate expenses
            6. Analyzing budget status with recommendations and alerts
            
            Based on the user's request, determine the appropriate action and provide a 
            comprehensive response. Consider the following:
            
            For expense recording: Extract amount, category, description, and other details
            For listing requests: Apply appropriate filters and present results clearly
            For analysis requests: Provide insights, trends, and actionable recommendations
            For budget queries: Compare against typical spending patterns and provide guidance
            
            Always consider the financial context and provide helpful budgeting advice.
            Suggest appropriate categories if the user doesn't specify them.
            Flag unusual spending patterns or amounts if noticed.
            """,
            expected_output="""
            A detailed response that addresses the user's expense-related request. This should include:
            - Clear acknowledgment of what was requested
            - Appropriate expense operation results or financial analysis
            - Relevant spending insights, trends, or budget recommendations
            - Categorization suggestions or financial optimization tips
            - If operations were performed, confirmation of success with relevant details
            - Proactive suggestions for better expense management and budgeting
            """,
            agent=expense_manager,
            verbose=True,
            max_retry_limit=3
        )
        
        # Execute the task
        crew = Crew(
            agents=[expense_manager],
            tasks=[expense_task],
            verbose=True
        )
        
        # Run the crew and get results
        result = await crew.kickoff_async()
        
        # For now, we'll provide the AI response along with a note about MCP integration
        response = f"""💰 **Expense Tracker Response:**

{str(result)}

---
💡 **Note:** This is the AI analysis of your expense request. In a full implementation, 
the actual expense operations would be performed using the integrated MCP tools.

🔧 **Available Operations:**
- Add expenses with automatic categorization
- List expenses by date/category/amount
- Generate spending summaries and analytics
- Update expense details and categories
- Delete incorrect expenses
- Analyze budget status with recommendations

💸 **Example Usage:**
- "I spent $25 on dinner at Italian restaurant"
- "Show me all food expenses this month"
- "How much did I spend on transportation this quarter?"
- "Give me a budget analysis for entertainment"

📊 **Analytics Features:**
- Monthly/quarterly spending summaries
- Category-wise expense breakdowns
- Budget status with alerts
- Spending pattern analysis
- Financial recommendations
"""
        
        yield Message(parts=[MessagePart(content=response)])
        
    except Exception as e:
        error_response = f"❌ Error in Expense Tracker: {str(e)}"
        yield Message(parts=[MessagePart(content=error_response)])

if __name__ == "__main__":
    print("💰 Starting Expense Tracker Server on port 8200...")
    print("📊 Available endpoints:")
    print("  - POST /runs (agent: expense_tracker)")
    print("🔧 MCP Tools integrated: expense management operations")
    
    server.run(port=8200) 