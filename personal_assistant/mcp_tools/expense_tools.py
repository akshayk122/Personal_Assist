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
from utils.data_manager import DataManager
from utils.supabase_config import supabase_manager

# Initialize MCP server
mcp = FastMCP()
data_manager = DataManager()

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
        amount: Expense amount (e.g., 25.50)
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
        
        # Try to add to Supabase first, fallback to JSON if Supabase fails
        try:
            print("[MCP Tool] Checking Supabase connection...")
            print(f"[MCP Tool] Supabase URL: {'SET' if supabase_manager.supabase_url else 'MISSING'}")
            print(f"[MCP Tool] Supabase Key: {'SET' if supabase_manager.supabase_key else 'MISSING'}")
            print(f"[MCP Tool] Supabase Client: {'INITIALIZED' if supabase_manager.client else 'NOT INITIALIZED'}")
            
            if supabase_manager.is_connected():
                print("[MCP Tool] Supabase connected, attempting to add expense...")
                expense_id = supabase_manager.add_expense(expense_data)
                print(f"[MCP Tool] Successfully added to Supabase with ID: {expense_id}")
                return f"Expense of ${amount:.2f} for '{description}' added to Supabase with ID: {expense_id}"
            else:
                print("[MCP Tool] Supabase not connected, attempting to reinitialize...")
                # Try to reinitialize the connection
                supabase_manager._initialize_client()
                if supabase_manager.is_connected():
                    print("[MCP Tool] Reinitialized successfully, adding expense...")
                    expense_id = supabase_manager.add_expense(expense_data)
                    print(f"[MCP Tool] Successfully added to Supabase with ID: {expense_id}")
                    return f"Expense of ${amount:.2f} for '{description}' added to Supabase with ID: {expense_id}"
                else:
                    print("[MCP Tool] Reinitialization failed, falling back to JSON...")
                    # Fallback to JSON file
                    expense_id = data_manager.add_expense(expense_data)
                    print(f"[MCP Tool] Added to JSON with ID: {expense_id}")
                    return f"Expense of ${amount:.2f} for '{description}' added to local storage with ID: {expense_id} (Supabase not available)"
        except Exception as db_error:
            # Fallback to JSON file if Supabase fails
            expense_id = data_manager.add_expense(expense_data)
            return f"Expense of ${amount:.2f} for '{description}' added to local storage with ID: {expense_id} (Database error: {str(db_error)})"
        
    except ValueError as e:
        return f"Invalid amount format: {str(e)}"
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
        # Try to get from Supabase first, fallback to JSON if needed
        try:
            if supabase_manager.is_connected():
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
                data_source = "Supabase"
            else:
                # Fallback to JSON file
                expenses = data_manager.get_expenses()
                
                # Apply filters manually for JSON data
                if start_date:
                    expenses = [e for e in expenses if e["date"] >= start_date]
                if end_date:
                    expenses = [e for e in expenses if e["date"] <= end_date]
                if category != "all":
                    expenses = [e for e in expenses if e["category"] == category.lower()]
                
                expenses = [e for e in expenses if min_amount <= e["amount"] <= max_amount]
                data_source = "Local Storage"
        except Exception as db_error:
            # Fallback to JSON file if Supabase fails
            expenses = data_manager.get_expenses()
            
            # Apply filters manually for JSON data
            if start_date:
                expenses = [e for e in expenses if e["date"] >= start_date]
            if end_date:
                expenses = [e for e in expenses if e["date"] <= end_date]
            if category != "all":
                expenses = [e for e in expenses if e["category"] == category.lower()]
            
            expenses = [e for e in expenses if min_amount <= e["amount"] <= max_amount]
            data_source = f"Local Storage (DB Error: {str(db_error)})"
        
        if not expenses:
            return "💰 No expenses found for the specified criteria."
        
        # Calculate total
        total_amount = sum(e["amount"] for e in expenses)
        
        # Sort by date (newest first)
        expenses.sort(key=lambda x: x["date"], reverse=True)
        
        # Format expenses list
        result = f"💰 Found {len(expenses)} expense(s) | Total: ${total_amount:.2f} | Source: {data_source}\n\n"
        
        for expense in expenses:
            tags_str = ", ".join(expense.get("tags", []))
            result += f"${expense['amount']:.2f} - {expense['description']}\n"
            result += f" {expense['date']}\n"
            result += f"   Category: {expense['category'].title()}"
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
        
        # Try to get summary from Supabase first
        try:
            if supabase_manager.is_connected():
                filters = {"start_date": start_date} if start_date else None
                summary = supabase_manager.get_expense_summary(filters)
                data_source = "Supabase"
                
                if summary["total_expenses"] == 0:
                    return "No expenses found to summarize."
            else:
                # Fallback to JSON file processing
                expenses = data_manager.get_expenses()
                
                if not expenses:
                    return "No expenses found to summarize."
                
                # Filter by date if needed
                if start_date:
                    expenses = [e for e in expenses if e["date"] >= start_date]
                
                # Calculate summary manually
                total_amount = sum(e["amount"] for e in expenses)
                total_expenses = len(expenses)
                
                # Category breakdown
                categories = {}
                for expense in expenses:
                    category = expense["category"]
                    if category not in categories:
                        categories[category] = {"count": 0, "amount": 0.0}
                    categories[category]["count"] += 1
                    categories[category]["amount"] += expense["amount"]
                
                summary = {
                    "total_expenses": total_expenses,
                    "total_amount": total_amount,
                    "categories": categories,
                    "average_expense": total_amount / total_expenses if total_expenses > 0 else 0.0
                }
                data_source = "Local Storage"
        except Exception as db_error:
            # Fallback to JSON processing if Supabase fails
            expenses = data_manager.get_expenses()
            
            if not expenses:
                return "No expenses found to summarize."
            
            # Filter by date if needed
            if start_date:
                expenses = [e for e in expenses if e["date"] >= start_date]
            
            # Calculate summary manually
            total_amount = sum(e["amount"] for e in expenses)
            total_expenses = len(expenses)
            
            # Category breakdown
            categories = {}
            for expense in expenses:
                category = expense["category"]
                if category not in categories:
                    categories[category] = {"count": 0, "amount": 0.0}
                categories[category]["count"] += 1
                categories[category]["amount"] += expense["amount"]
            
            summary = {
                "total_expenses": total_expenses,
                "total_amount": total_amount,
                "categories": categories,
                "average_expense": total_amount / total_expenses if total_expenses > 0 else 0.0
            }
            data_source = f"Local Storage (DB Error: {str(db_error)})"
        
        # Format the summary response using the calculated summary
        result = f"Expense Summary - Last {period.title()} | Source: {data_source}\n"
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
        # Parse updates JSON
        update_data = json.loads(updates)
        
        success = data_manager.update_expense(expense_id, update_data)
        
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
        success = data_manager.delete_expense(expense_id)
        
        if success:
            return f"Expense {expense_id} deleted successfully."
        else:
            return f"Expense {expense_id} not found."
            
    except Exception as e:
        return f"Error deleting expense: {str(e)}"

@mcp.tool()
def get_budget_status(category: str = "all", period: str = "month") -> str:
    """Get budget status and spending analysis
    
    Args:
        category: Category to analyze or 'all' (default: all)
        period: Time period (week|month|quarter|year) (default: month)
    
    Returns:
        str: Budget analysis and recommendations
    
    Example:
        get_budget_status("food", "month")
    """
    try:
        expenses = data_manager.get_expenses()
        
        # Calculate date range based on period
        now = datetime.now()
        if period == "week":
            start_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
            period_label = "this week"
        elif period == "month":
            start_date = now.replace(day=1).strftime("%Y-%m-%d")
            period_label = "this month"
        elif period == "quarter":
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            start_date = now.replace(month=quarter_start_month, day=1).strftime("%Y-%m-%d")
            period_label = "this quarter"
        elif period == "year":
            start_date = now.replace(month=1, day=1).strftime("%Y-%m-%d")
            period_label = "this year"
        else:
            start_date = ""
            period_label = "all time"
        
        # Filter expenses by period and category
        filtered_expenses = expenses
        if start_date:
            filtered_expenses = [e for e in filtered_expenses if e["date"] >= start_date]
        if category != "all":
            filtered_expenses = [e for e in filtered_expenses if e["category"] == category.lower()]
        
        if not filtered_expenses:
            return f"💰 No expenses found for {category} {period_label}."
        
        # Calculate spending
        total_spent = sum(e["amount"] for e in filtered_expenses)
        transaction_count = len(filtered_expenses)
        avg_per_transaction = total_spent / transaction_count if transaction_count > 0 else 0
        
        # Simple budget recommendations (these could be made configurable)
        budget_limits = {
            "food": {"week": 150, "month": 600, "quarter": 1800, "year": 7200},
            "transportation": {"week": 75, "month": 300, "quarter": 900, "year": 3600},
            "entertainment": {"week": 100, "month": 400, "quarter": 1200, "year": 4800},
            "utilities": {"week": 50, "month": 200, "quarter": 600, "year": 2400},
            "healthcare": {"week": 25, "month": 100, "quarter": 300, "year": 1200},
            "shopping": {"week": 125, "month": 500, "quarter": 1500, "year": 6000},
            "other": {"week": 50, "month": 200, "quarter": 600, "year": 2400}
        }
        
        result = f"Budget Status for {category.title()} - {period_label.title()}\n\n"
        result += f"Total Spent: ${total_spent:.2f}\n"
        result += f"Transactions: {transaction_count}\n"
        result += f"Average per Transaction: ${avg_per_transaction:.2f}\n\n"
        
        # Budget analysis for specific category
        if category != "all" and category in budget_limits and period in budget_limits[category]:
            budget_limit = budget_limits[category][period]
            remaining = budget_limit - total_spent
            percentage_used = (total_spent / budget_limit) * 100
            
            result += f"Suggested Budget: ${budget_limit:.2f}\n"
            result += f"Amount Used: ${total_spent:.2f} ({percentage_used:.1f}%)\n"
            result += f"Remaining: ${remaining:.2f}\n\n"
            
            # Recommendations
            if percentage_used < 50:
                result += "Great job! You're well within budget.\n"
            elif percentage_used < 80:
                result += "You're on track but monitor spending.\n"
            elif percentage_used < 100:
                result += "Warning: You're approaching your budget limit.\n"
            else:
                result += "Alert: You've exceeded the suggested budget!\n"
        else:
            result += "Tip: Consider setting a budget for better expense tracking.\n"
        
        return result
        
    except Exception as e:
        return f"Error getting budget status: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio") 