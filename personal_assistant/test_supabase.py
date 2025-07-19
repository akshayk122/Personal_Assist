#!/usr/bin/env python3
"""
Test script to verify Supabase connection and functionality
Run this to check if your Supabase integration is working correctly
"""

import os
import sys
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

def test_environment_variables():
    """Test if environment variables are set"""
    print(f"{Fore.CYAN}{Style.BRIGHT}🔧 Testing Environment Variables...")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_API_KEY")
    
    if supabase_url:
        print(f"{Fore.GREEN}✅ SUPABASE_URL is set: {supabase_url[:50]}...")
    else:
        print(f"{Fore.RED}❌ SUPABASE_URL is not set")
        return False
    
    if supabase_key:
        print(f"{Fore.GREEN}✅ SUPABASE_API_KEY is set: {supabase_key[:20]}...")
    else:
        print(f"{Fore.RED}❌ SUPABASE_API_KEY is not set")
        return False
    
    return True

def test_supabase_import():
    """Test if Supabase library is installed"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}📦 Testing Supabase Library Import...")
    
    try:
        from supabase import create_client, Client
        print(f"{Fore.GREEN}✅ Supabase library imported successfully")
        return True
    except ImportError as e:
        print(f"{Fore.RED}❌ Failed to import Supabase library: {str(e)}")
        print(f"{Fore.YELLOW}💡 Try running: uv sync or pip install supabase")
        return False

def test_supabase_connection():
    """Test basic Supabase connection"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}🔗 Testing Supabase Connection...")
    
    try:
        from utils.supabase_config import supabase_manager
        
        if supabase_manager.is_connected():
            print(f"{Fore.GREEN}✅ Supabase client initialized successfully")
            return True
        else:
            print(f"{Fore.RED}❌ Supabase client failed to initialize")
            print(f"{Fore.YELLOW}💡 Check your credentials and internet connection")
            return False
    except Exception as e:
        print(f"{Fore.RED}❌ Error testing connection: {str(e)}")
        return False

def test_database_operations():
    """Test basic database operations"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}💾 Testing Database Operations...")
    
    try:
        from utils.supabase_config import supabase_manager
        
        if not supabase_manager.is_connected():
            print(f"{Fore.RED}❌ Skipping database tests - no connection")
            return False
        
        # Test adding a test expense
        test_expense = {
            "amount": 1000.00,
            "currency": "USD",
            "category": "Electronics",
            "subcategory": "connection-test",
            "description": "Test expense for connection verification",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "payment_method": "test",
            "is_recurring": False,
            "tags": ["test", "connection-check", "Electronics"]
        }
        
        print(f"{Fore.YELLOW}🧪 Adding test expense...")
        expense_id = supabase_manager.add_expense(test_expense)
        print(f"{Fore.GREEN}✅ Test expense added with ID: {expense_id}")
        
        # Test retrieving expenses
        print(f"{Fore.YELLOW}📋 Retrieving expenses...")
        expenses = supabase_manager.get_expenses({"category": "test"})
        print(f"{Fore.GREEN}✅ Retrieved {len(expenses)} test expenses")
        
        # Test deleting the test expense
        print(f"{Fore.YELLOW}🗑️ Cleaning up test expense...")
        deleted = supabase_manager.delete_expense(expense_id)
        if deleted:
            print(f"{Fore.GREEN}✅ Test expense deleted successfully")
        else:
            print(f"{Fore.YELLOW}⚠️ Test expense deletion status unclear")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Database operation failed: {str(e)}")
        return False

def test_expense_tools():
    """Test the expense tools integration"""
    print(f"\n{Fore.CYAN}{Style.BRIGHT}🛠️ Testing Expense Tools Integration...")
    
    try:
        from mcp_tools.expense_tools import add_expense, list_expenses
        
        # Test adding an expense through the tools
        print(f"{Fore.YELLOW}💸 Testing add_expense tool...")
        result = add_expense(
            amount=122.50,
            category="Electronics",
            description="Connection test expense via tools",
            payment_method="test",
            subcategory="tool-test",
            tags="test,integration,Electronics"
        )
        print(f"{Fore.GREEN}✅ Add expense result: {result}")
        
        # Test listing expenses
        print(f"{Fore.YELLOW}📋 Testing list_expenses tool...")
        result = list_expenses(category="test")
        print(f"{Fore.GREEN}✅ List expenses working")
        
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Expense tools test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print(f"{Fore.MAGENTA}{Style.BRIGHT}🧪 Supabase Connection Test Suite")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("Supabase Library", test_supabase_import),
        ("Connection", test_supabase_connection),
        ("Database Operations", test_database_operations),
        ("Expense Tools", test_expense_tools)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"{Fore.RED}❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{Fore.CYAN}{Style.BRIGHT}📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        if result:
            print(f"{Fore.GREEN}✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"{Fore.RED}❌ {test_name}: FAILED")
    
    print(f"\n{Fore.CYAN}📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"{Fore.GREEN}{Style.BRIGHT}🎉 All tests passed! Supabase integration is working correctly.")
        print(f"{Fore.GREEN}💡 You can now use Supabase for expense storage!")
    elif passed >= 3:
        print(f"{Fore.YELLOW}{Style.BRIGHT}⚠️ Basic functionality working, but some advanced features may have issues.")
        print(f"{Fore.YELLOW}💡 Check the failed tests above for details.")
    else:
        print(f"{Fore.RED}{Style.BRIGHT}❌ Multiple tests failed. Supabase integration needs attention.")
        print(f"{Fore.RED}💡 Check your environment variables and Supabase setup.")
    
    print(f"\n{Fore.CYAN}📚 For setup help, see: SUPABASE_SETUP.md")

if __name__ == "__main__":
    main() 