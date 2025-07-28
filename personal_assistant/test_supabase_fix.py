#!/usr/bin/env python3
"""
Test script to verify Supabase connection and RLS policies
Run this after applying the RLS fix to verify everything works
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test basic Supabase connection"""
    print("🔍 Testing Supabase Connection...")
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_API_KEY")
    
    print(f"SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
    print(f"SUPABASE_API_KEY: {'✅ Set' if supabase_key else '❌ Missing'}")
    
    if not supabase_url or not supabase_key:
        print("❌ Environment variables not set properly")
        print("Please check your .env file")
        return False
    
    try:
        from utils.supabase_config import supabase_manager
        
        if supabase_manager.is_connected():
            print("✅ Supabase client initialized successfully")
            return True
        else:
            print("❌ Supabase client failed to initialize")
            return False
            
    except Exception as e:
        print(f"❌ Error initializing Supabase: {str(e)}")
        return False

def test_database_operations():
    """Test basic database operations"""
    print("\n🔍 Testing Database Operations...")
    
    try:
        from utils.supabase_config import supabase_manager
        
        # Test 1: Add a test note
        print("Testing note addition...")
        test_note_data = {
            "content": "Test note for RLS policy verification",
            "iscompleted": False
        }
        
        note_id = supabase_manager.add_note(test_note_data)
        print(f"✅ Note added successfully with ID: {note_id}")
        
        # Test 2: Retrieve notes
        print("Testing note retrieval...")
        notes = supabase_manager.get_notes("test")
        print(f"✅ Retrieved {len(notes)} notes")
        
        # Test 3: Add a test expense
        print("Testing expense addition...")
        test_expense_data = {
            "amount": 10.00,
            "currency": "USD",
            "category": "test",
            "description": "Test expense for RLS verification",
            "date": "2024-12-16",
            "payment_method": "credit"
        }
        
        expense_id = supabase_manager.add_expense(test_expense_data)
        print(f"✅ Expense added successfully with ID: {expense_id}")
        
        # Test 4: Retrieve expenses
        print("Testing expense retrieval...")
        expenses = supabase_manager.get_expenses()
        print(f"✅ Retrieved {len(expenses)} expenses")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operation failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Supabase RLS Policy Test")
    print("=" * 40)
    
    # Test 1: Connection
    connection_ok = test_supabase_connection()
    
    if not connection_ok:
        print("\n❌ Connection test failed. Please check your setup.")
        return
    
    # Test 2: Database operations
    operations_ok = test_database_operations()
    
    if operations_ok:
        print("\n🎉 All tests passed! Your Supabase setup is working correctly.")
        print("You can now use the personal assistant without RLS policy errors.")
    else:
        print("\n❌ Database operations failed. Please run the RLS fix script.")
        print("See RLS_TROUBLESHOOTING.md for detailed instructions.")

if __name__ == "__main__":
    main() 