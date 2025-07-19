import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

"""
ACP Server 2 - Expense Tracker Agent with MCP tools
Port: 8200

Handles all expense-related operations using MCP tools
Following the pattern from acp_demo.py
"""

import os
from dotenv import load_dotenv
from collections.abc import AsyncGenerator

# Load environment variables
load_dotenv()
print(f"[Expense Server] Environment check:")
print(f"SUPABASE_URL: {'SET' if os.getenv('SUPABASE_URL') else 'MISSING'}")
print(f"SUPABASE_API_KEY: {'SET' if os.getenv('SUPABASE_API_KEY') else 'MISSING'}")
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
        user_query = input[0].parts[0].content.lower()
        logger.debug(f"Processing user query: {user_query}")
        
        try:
            # Direct expense operations without AI analysis
            if "$" in user_query or "spent" in user_query or "add" in user_query:
                # Extract amount
                import re
                amount_match = re.search(r'\$?(\d+\.?\d*)', user_query)
                if not amount_match:
                    yield Message(parts=[MessagePart(content="Could not find an amount in your request. Please specify the amount (e.g., $50).")])
                    return
                
                amount = float(amount_match.group(1))
                
                # Extract category and description
                # Remove the amount part to avoid confusion
                text_without_amount = user_query.replace(amount_match.group(0), "").strip()
                print(f"[Expense Server] Processing text: '{text_without_amount}'")
                
                # Look for category keywords
                categories = {
                    "electronics": ["electronics", "gadget", "device", "computer", "phone", "laptop"],
                    "food": ["food", "lunch", "dinner", "breakfast", "meal", "restaurant", "grocery"],
                    "transportation": ["transport", "gas", "fuel", "bus", "train", "taxi", "uber"],
                    "entertainment": ["entertainment", "movie", "game", "concert", "show"],
                    "utilities": ["utility", "electricity", "water", "internet", "phone bill"],
                    "healthcare": ["health", "medical", "doctor", "medicine", "pharmacy"],
                    "shopping": ["shopping", "clothes", "clothing", "shoes", "accessories"]
                }
                print("[Expense Server] Looking for category keywords...")
                
                # Find category from text
                found_category = None
                for cat, keywords in categories.items():
                    if any(keyword in text_without_amount for keyword in keywords):
                        found_category = cat
                        print(f"[Expense Server] Found category: {cat} (matched keywords: {[k for k in keywords if k in text_without_amount]})")
                        break
                
                category = found_category or "other"
                description = text_without_amount
                print(f"[Expense Server] Final category: {category}")
                
                logger.debug(f"Extracted: amount={amount}, category={category}, description={description}")
                
                # Add the expense
                try:
                    expense_result = add_expense(
                        amount=amount,
                        category=category,
                        description=description
                    )
                    yield Message(parts=[MessagePart(content=expense_result)])
                    return
                except Exception as e:
                    logger.error(f"Error adding expense: {str(e)}")
                    yield Message(parts=[MessagePart(content=f"Error adding expense: {str(e)}")])
            
            # Handle list/show expenses
            elif "list" in user_query or "show" in user_query:
                result = list_expenses()
                yield Message(parts=[MessagePart(content=result)])
                return
            
            # Handle summary requests
            elif "summary" in user_query:
                result = get_expense_summary()
                yield Message(parts=[MessagePart(content=result)])
                return
            
            # Default help message
            else:
                help_message = """💰 **Expense Tracker Help**

Please use one of these formats:
1. Add expense: "Add $X for Y" (e.g., "Add $50 for electronics")
2. List expenses: "Show my expenses" or "List expenses"
3. Get summary: "Show expense summary"

Available categories: electronics, food, transportation, entertainment, utilities, healthcare, shopping"""
                yield Message(parts=[MessagePart(content=help_message)])
                return
                
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            yield Message(parts=[MessagePart(content=f"Error: {str(e)}")])
        except Exception as e:
            response = f"""**Expense Tracker Response:**
Error processing expense: {str(e)}

{str(result)}
"""
        
        yield Message(parts=[MessagePart(content=response)])
        
    except Exception as e:
        error_response = f" Error in Expense Tracker: {str(e)}"
        yield Message(parts=[MessagePart(content=error_response)])

if __name__ == "__main__":
    print("Starting Expense Tracker Server on port 8200...")
    print("Available endpoints:")
    print("POST /runs (agent: expense_tracker)")
    print("MCP Tools integrated: expense management operations")
    
    server.run(port=8200) 