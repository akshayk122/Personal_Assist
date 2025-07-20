"""
MCP Tools for Expense Management
Following the pattern from the existing MCP server setup
"""

from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import sys
import os
from collections import defaultdict

# Add parent directory to path to import utils
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.supabase_config import supabase_manager

# Initialize MCP server
mcp = FastMCP()

@mcp.tool()
def add_expense(
    amount: float,
    category: str,
    description: str,
    date: str = "",
    payment_method: str = "credit",
    subcategory: str = "",
    tags: str = ""
) -> str:
    """Add a new expense to the tracker
    
    Args:
        amount: Expense amount (e.g.,25.50)
        category: Expense category (food|transportation|entertainment|utilities|healthcare|shopping|electronics|other)
        description: Description of the expense
        date: Expense date in YYYY-MM-DD format (default: today)
        payment_method: Payment method (cash|credit|debit|online) (default: credit)
        subcategory: Subcategory for better organization (optional)
        tags: Comma-separated tags (optional)
    
    Returns:
        str: Success message with expense ID
    
    Example:
        add_expense(12.50, "food", "Subway sandwich", "2024-01-15", "credit", "lunch", "quick-meal")
    """
    print(f"[MCP Tool] add_expense called with: amount={amount}, category={category}, description={description}")
    try:
        # Use today's date if not provided
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        expense_data = {
            "amount": float(amount),
            "currency": "USD",
            "category": category.lower(),
            "subcategory": subcategory,
            "description": description,
            "date": date,
            "payment_method": payment_method.lower(),
            "is_recurring": False,
            "tags": tag_list
        }
        print(f"[MCP Tool] Prepared expense data: {expense_data}")
        
        if not supabase_manager.is_connected():
            raise Exception("Database not available. Please check your Supabase configuration.")
            
        expense_id = supabase_manager.add_expense(expense_data)
        print(f"[MCP Tool] Successfully added to Supabase with ID: {expense_id}")
        return f"Expense of ${amount:.2f} for '{description}' added with ID: {expense_id}"
        
    except Exception as e:
        return f"Error adding expense: {str(e)}"

@mcp.tool()
def list_expenses(
    start_date: str = "",
    end_date: str = "",
    category: str = "all",
    min_amount: float = 0,
    max_amount: float = 999999
) -> str:
    """List expenses within specified filters
    
    Args:
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        category: Filter by category or 'all' (default: all)
        min_amount: Minimum amount filter (default: 0)
        max_amount: Maximum amount filter (default: 999999)
    
    Returns:
        str: Formatted list of expenses
    
    Example:
        list_expenses("2024-01-01", "2024-01-31", "food", 10, 50)
    """
    try:
        if not supabase_manager.is_connected():
            raise Exception("Database not available. Please check your Supabase configuration.")
            
        # Build filters for Supabase
        filters = {}
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        if category != "all":
            filters["category"] = category.lower()
        if min_amount > 0:
            filters["min_amount"] = min_amount
        if max_amount < 999999:
            filters["max_amount"] = max_amount
        
        expenses = supabase_manager.get_expenses(filters)
        
        if not expenses:
            return "💰 No expenses found for the specified criteria."
        
        # Calculate total
        total_amount = sum(e["amount"] for e in expenses)
        
        # Format expenses list
        result = f"💰 Found {len(expenses)} expense(s) | Total: ${total_amount:.2f}\n\n"
        
        for expense in expenses:
            tags_str = ", ".join(expense.get("tags", []))
            result += f"${expense['amount']:.2f} - {expense['description']}\n"
            result += f"Date: {expense['date']}\n"
            result += f"Category: {expense['category'].title()}"
            if expense.get("subcategory"):
                result += f" > {expense['subcategory']}"
            result += "\n"
            result += f"Payment: {expense['payment_method'].title()}\n"
            if tags_str:
                result += f"Tags: {tags_str}\n"
            result += f"ID: {expense['expense_id']}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error listing expenses: {str(e)}"

@mcp.tool()
def filter_expenses(category: str) -> str:
    """Filter expenses by category
    
    Args:
        category: Category to filter by (food|transportation|entertainment|utilities|healthcare|shopping|electronics|other)
    
    Returns:
        str: Formatted list of filtered expenses
    
    Example:
        filter_expenses("food")
    """
    try:
        if not supabase_manager.is_connected():
            raise Exception("Database not available. Please check your Supabase configuration.")
            
        # Build filters for category
        filters = {"category": category.lower()}
        print(f"[MCP Tool] Filtering expenses by category: {category}")
        
        expenses = supabase_manager.get_expenses(filters)
        
        if not expenses:
            return f"No expenses found for category: {category}"
        
        # Calculate total
        total_amount = sum(e["amount"] for e in expenses)
        
        # Format expenses list
        result = f"Found {len(expenses)} expense(s) for category '{category}' | Total: ${total_amount:.2f}\n\n"
        
        for expense in expenses:
            tags_str = ", ".join(expense.get("tags", []))
            result += f"${expense['amount']:.2f} - {expense['description']}\n"
            result += f"Date: {expense['date']}\n"
            result += f"Payment: {expense['payment_method'].title()}\n"
            if tags_str:
                result += f"Tags: {tags_str}\n"
            result += f"ID: {expense['expense_id']}\n\n"
        
        return result
        
    except Exception as e:
        return f"Error filtering expenses: {str(e)}"

@mcp.tool()
def get_expense_summary(period: str = "month", group_by: str = "category") -> str:
    """Get expense summary and analytics
    
    Args:
        period: Time period (week|month|quarter|year) (default: month)
        group_by: Group expenses by (category|date|payment_method) (default: category)
    
    Returns:
        str: Formatted expense summary
    
    Example:
        get_expense_summary("month", "category")
    """
    try:
        if not supabase_manager.is_connected():
            raise Exception("Database not available. Please check your Supabase configuration.")
            
        # Calculate date range based on period
        now = datetime.now()
        if period == "week":
            start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        elif period == "month":
            start_date = now.replace(day=1).strftime("%Y-%m-%d")
        elif period == "quarter":
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_start_month, day=1).strftime("%Y-%m-%d")
        elif period == "year":
            start_date = now.replace(month=1, day=1).strftime("%Y-%m-%d")
        else:
            start_date = None
        
        filters = {"start_date": start_date} if start_date else None
        summary = supabase_manager.get_expense_summary(filters)
        
        if summary["total_expenses"] == 0:
            return "No expenses found to summarize."
        
        # Format the summary response
        result = f"Expense Summary - Last {period.title()}\n"
        result += f"Total Spent: ${summary['total_amount']:.2f}\n"
        result += f"Number of Transactions: {summary['total_expenses']}\n"
        result += f"Average per Transaction: ${summary['average_expense']:.2f}\n\n"
        
        result += f"Breakdown by Category:\n"
        
        # Sort categories by amount (highest first)
        sorted_categories = sorted(summary['categories'].items(), key=lambda x: x[1]['amount'], reverse=True)
        
        for category_name, category_data in sorted_categories:
            percentage = (category_data['amount'] / summary['total_amount']) * 100
            result += f"{category_name.title()}: ${category_data['amount']:.2f} ({percentage:.1f}%) - {category_data['count']} transactions\n"
        
        return result
        
    except Exception as e:
        return f"Error generating expense summary: {str(e)}"

@mcp.tool()
def update_expense(expense_id: str, updates: str) -> str:
    """Update an expense's details
    
    Args:
        expense_id: The expense ID to update
        updates: JSON string with updates (e.g., '{"amount": 15.75, "category": "food"}')
    
    Returns:
        str: Success or error message
    
    Example:
        update_expense("e001", '{"amount": 15.75, "description": "Updated lunch cost"}')
    """
    try:
        if not supabase_manager.is_connected():
            raise Exception("Database not available. Please check your Supabase configuration.")
            
        # Parse updates JSON
        update_data = json.loads(updates)
        
        success = supabase_manager.update_expense(expense_id, update_data)
        
        if success:
            return f"Expense {expense_id} updated successfully."
        else:
            return f"Expense {expense_id} not found."
            
    except json.JSONDecodeError:
        return "Invalid JSON format for updates."
    except Exception as e:
        return f"Error updating expense: {str(e)}"

@mcp.tool()
def delete_expense(expense_id: str) -> str:
    """Delete an expense
    
    Args:
        expense_id: The expense ID to delete
    
    Returns:
        str: Success or error message
    
    Example:
        delete_expense("e001")
    """
    try:
        if not supabase_manager.is_connected():
            raise Exception("Database not available. Please check your Supabase configuration.")
            
        success = supabase_manager.delete_expense(expense_id)
        
        if success:
            return f"Expense {expense_id} deleted successfully."
        else:
            return f"Expense {expense_id} not found."
            
    except Exception as e:
        return f"Error deleting expense: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio") 