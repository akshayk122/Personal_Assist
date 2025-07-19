#!/usr/bin/env python3
"""
Test Supabase Connection and Setup
"""

import os
from utils.supabase_config import supabase_manager
from mcp_tools.expense_tools import add_expense, list_expenses

def test_supabase():
    """Test Supabase connection and operations"""
    print("\n=== Testing Supabase Configuration ===")
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_API_KEY")
    
    print(f"\nEnvironment Variables:")
    print(f"SUPABASE_URL: {'SET' if supabase_url else 'MISSING'}")
    print(f"SUPABASE_API_KEY: {'SET' if supabase_key else 'MISSING'}")
    
    # Check connection
    print("\nTesting Connection:")
    is_connected = supabase_manager.is_connected()
    print(f"Supabase Connected: {is_connected}")
    
    if not is_connected:
        print("❌ Supabase connection failed. Please check your credentials.")
        return
    
    # Test expense operations
    print("\nTesting Expense Operations:")
    try:
        # Add test expense
        print("\n1. Adding test expense...")
        result = add_expense(
            amount=10.00,
            category="test",
            description="Test expense"
        )
        print(f"Result: {result}")
        
        # List expenses
        print("\n2. Listing expenses...")
        expenses = list_expenses()
        print(f"Result: {expenses}")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")

if __name__ == "__main__":
    test_supabase() 