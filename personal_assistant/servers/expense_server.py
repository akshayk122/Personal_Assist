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
from datetime import datetime, timedelta
import re
from dateutil import parser
from dateutil.relativedelta import relativedelta
import json

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
    update_expense, delete_expense, get_budget_status,
    filter_expenses
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

def extract_date_from_text(text: str) -> str:
    """Extract date from natural language text"""
    text = text.lower()
    today = datetime.now()
    
    # Handle relative dates
    if "yesterday" in text:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    elif "today" in text:
        return today.strftime("%Y-%m-%d")
    elif "tomorrow" in text:
        # Don't allow future dates
        return today.strftime("%Y-%m-%d")
    elif "last week" in text:
        return (today - timedelta(days=7)).strftime("%Y-%m-%d")
    elif "next week" in text:
        # Don't allow future dates
        return today.strftime("%Y-%m-%d")
    
    # Try to find date patterns
    try:
        # Look for dates like "March 15", "15th March", "03/15", "15-03", etc.
        date_match = re.search(r'\b(\d{1,2}[-/]\d{1,2}(?:[-/]\d{2,4})?|\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)|(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?(?:\s+\d{2,4})?)\b', text)
        
        if date_match:
            parsed_date = parser.parse(date_match.group(0), fuzzy=True)
            # If year is not specified, use current year
            if parsed_date.year == 1900:
                parsed_date = parsed_date.replace(year=today.year)
            # Don't allow future dates
            if parsed_date > today:
                parsed_date = parsed_date.replace(year=today.year)
                if parsed_date > today:
                    return today.strftime("%Y-%m-%d")
            return parsed_date.strftime("%Y-%m-%d")
    except Exception:
        pass
    
    # Default to today if no date found
    return today.strftime("%Y-%m-%d")

@server.agent(name="expense_tracker")
async def expense_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    try:
        # Extract user query
        user_query = input[0].parts[0].content.lower()
        logger.debug(f"Processing user query: {user_query}")
        
        try:
            # Handle expense updates
            if "update" in user_query or "change" in user_query or "fix" in user_query:
                # Look for expense ID
                import re
                id_match = re.search(r'(?:id|ID):\s*([a-f0-9-]+)', user_query)
                if id_match:
                    expense_id = id_match.group(1)
                    print(f"[Expense Server] Found expense ID: {expense_id}")
                    
                    # Look for category keywords
                    categories = {
                        "transportation": ["transport", "cab", "taxi", "uber", "lyft", "ride", "auto", "rickshaw"],
                        "food": ["food", "lunch", "dinner", "breakfast", "meal", "restaurant", "grocery", "snack", "cafe", "kfc"],
                        "electronics": ["electronics", "gadget", "device", "computer", "phone", "laptop", "tv", "television"],
                        "entertainment": ["entertainment", "movie", "game", "concert", "show", "theatre", "sports"],
                        "utilities": ["utility", "electricity", "water", "internet", "phone bill", "gas", "broadband"],
                        "healthcare": ["health", "medical", "doctor", "medicine", "pharmacy", "hospital", "clinic"],
                        "shopping": ["shopping", "clothes", "clothing", "shoes", "accessories", "fashion"]
                    }
                    
                    # Find category from text - first try exact matches
                    found_category = None
                    for cat in categories.keys():
                        if cat in user_query:
                            found_category = cat
                            print(f"[Expense Server] Found exact category match: {cat}")
                            break
                    
                    # If no exact match, try keywords
                    if not found_category:
                        for cat, keywords in categories.items():
                            if any(keyword in user_query for keyword in keywords):
                                found_category = cat
                                matching_keywords = [k for k in keywords if k in user_query]
                                print(f"[Expense Server] Found category {cat} via keywords: {matching_keywords}")
                                break
                    
                    if found_category:
                        # Update the expense
                        updates = {
                            "category": found_category.lower(),
                            "date": datetime.now().strftime("%Y-%m-%d")  # Also fix the date
                        }
                        try:
                            result = update_expense(expense_id, json.dumps(updates))
                            yield Message(parts=[MessagePart(content=f"Updated expense {expense_id} to category: {found_category}")])
                            return
                        except Exception as e:
                            logger.error(f"Error updating expense: {str(e)}")
                            yield Message(parts=[MessagePart(content=f"Error updating expense: {str(e)}")])
                            return
                    else:
                        yield Message(parts=[MessagePart(content="Could not determine which category to update to. Please specify a category.")])
                        return
                else:
                    yield Message(parts=[MessagePart(content="Please provide the expense ID to update (e.g., 'update expense ID: xxx to transportation')")])
                    return
            
            # Handle expense listing and filtering queries
            elif any(word in user_query for word in ["show", "list", "spent", "how much", "what's", "whats", "my", "filter"]):
                # Define categories with their variations
                categories = {
                    "transportation": ["transport", "tranport", "tranportation", "cab", "taxi", "uber", "lyft", "ride", "auto", "rickshaw"],
                    "food": ["food", "lunch", "dinner", "breakfast", "meal", "restaurant", "grocery", "snack", "cafe", "kfc"],
                    "electronics": ["electronics", "gadget", "device", "computer", "phone", "laptop", "tv", "television"],
                    "entertainment": ["entertainment", "movie", "game", "concert", "show", "theatre", "sports"],
                    "utilities": ["utility", "electricity", "water", "internet", "phone bill", "gas", "broadband"],
                    "healthcare": ["health", "medical", "doctor", "medicine", "pharmacy", "hospital", "clinic"],
                    "shopping": ["shopping", "clothes", "clothing", "shoes", "accessories", "fashion"]
                }
                
                # Find category from query
                found_category = None
                print(f"[Expense Server] Looking for category in query: '{user_query}'")
                
                # First try exact category matches
                for cat in categories.keys():
                    if cat in user_query:
                        found_category = cat
                        print(f"[Expense Server] Found exact category match: {cat}")
                        break
                
                # If no exact match, try keywords and variations
                if not found_category:
                    for cat, keywords in categories.items():
                        # Check for exact keyword matches first
                        if any(keyword == word for keyword in keywords for word in user_query.split()):
                            found_category = cat
                            print(f"[Expense Server] Found exact keyword match for category {cat}")
                            break
                        # Then check for partial matches
                        elif any(keyword in user_query for keyword in keywords):
                            found_category = cat
                            matching_keywords = [k for k in keywords if k in user_query]
                            print(f"[Expense Server] Found category {cat} via keywords: {matching_keywords}")
                            break
                
                # Use the filter_expenses tool if category found
                if found_category:
                    print(f"[Expense Server] Using filter_expenses tool for category: {found_category}")
                    try:
                        result = filter_expenses(found_category)
                        # Add a header to make the filtering more clear
                        result = f"Filtering expenses for category: {found_category.title()}\n\n{result}"
                    except Exception as e:
                        logger.error(f"Error using filter_expenses: {str(e)}")
                        # Fallback to list_expenses with filter if filter_expenses fails
                        result = list_expenses(category=found_category.lower())
                else:
                    print("[Expense Server] No specific category found, listing all expenses")
                    result = list_expenses()
                
                yield Message(parts=[MessagePart(content=result)])
                return
            
            # Handle adding new expenses
            elif "$" in user_query or "add" in user_query or "spent" in user_query:
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
                
                # Extract date from text
                expense_date = extract_date_from_text(text_without_amount)
                print(f"[Expense Server] Extracted date: {expense_date}")
                
                # Look for category keywords
                categories = {
                    "transportation": ["transport", "cab", "taxi", "uber", "lyft", "ride", "auto", "rickshaw"],
                    "food": ["food", "lunch", "dinner", "breakfast", "meal", "restaurant", "grocery", "snack", "cafe", "kfc"],
                    "electronics": ["electronics", "gadget", "device", "computer", "phone", "laptop", "tv", "television"],
                    "entertainment": ["entertainment", "movie", "game", "concert", "show", "theatre", "sports"],
                    "utilities": ["utility", "electricity", "water", "internet", "phone bill", "gas", "broadband"],
                    "healthcare": ["health", "medical", "doctor", "medicine", "pharmacy", "hospital", "clinic"],
                    "shopping": ["shopping", "clothes", "clothing", "shoes", "accessories", "fashion"]
                }
                print("[Expense Server] Looking for category keywords...")
                
                # Find category from text - first try exact matches
                found_category = None
                for cat in categories.keys():
                    if cat in text_without_amount:
                        found_category = cat
                        print(f"[Expense Server] Found exact category match: {cat}")
                        break
                
                # If no exact match, try keywords
                if not found_category:
                    for cat, keywords in categories.items():
                        if any(keyword in text_without_amount for keyword in keywords):
                            found_category = cat
                            matching_keywords = [k for k in keywords if k in text_without_amount]
                            print(f"[Expense Server] Found category {cat} via keywords: {matching_keywords}")
                            break
                
                category = found_category or "other"
                # Clean up description - remove extra whitespace and normalize
                description = ' '.join(text_without_amount.split())
                print(f"[Expense Server] Final category: {category}")
                
                logger.debug(f"Extracted: amount={amount}, category={category}, description={description}, date={expense_date}")
                
                # Add the expense
                try:
                    expense_result = add_expense(
                        amount=amount,
                        category=category,
                        description=description,
                        date=expense_date
                    )
                    yield Message(parts=[MessagePart(content=expense_result)])
                    return
                except Exception as e:
                    logger.error(f"Error adding expense: {str(e)}")
                    yield Message(parts=[MessagePart(content=f"Error adding expense: {str(e)}")])
            
            # Default help message
            else:
                help_message = """💰 **Expense Tracker Help**

Please use one of these formats:
1. Add expense: 
   - "Add $50 for electronics" (uses today's date)
   - "Spent $25 on food yesterday"
   - "Add $100 for shopping on March 15th"
2. View expenses:
   - "Show my food expenses"
   - "Filter transportation expenses"
   - "List expenses in transportation category"
   - "Show all expenses" (no category filter)
3. Update expense:
   - "Update expense ID: xxx to transportation"
   - "Change expense ID: xxx to food"
4. Get summary: "Show expense summary"

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