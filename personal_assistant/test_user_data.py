#!/usr/bin/env python3
"""
Test script to check user data filtering
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the personal_assistant directory to path
sys.path.append('personal_assistant')

from utils.supabase_config import SupabaseManager

def test_user_data():
    """Test what data is returned for different users"""
    
    print("🔍 Testing User Data Filtering")
    print("=" * 40)
    
    # Test with different user IDs
    user_ids = ["Akshay12", "akshay12", "AKSHAY12", "default_user", "test123"]
    
    for user_id in user_ids:
        print(f"\n🧪 Testing user: {user_id}")
        
        try:
            # Create Supabase manager for this user
            sm = SupabaseManager(user_id)
            
            if not sm.is_connected():
                print(f"❌ Could not connect to Supabase for {user_id}")
                continue
            
            # Get expenses for this user
            expenses = sm.get_expenses({}, user_id)
            
            print(f"✅ Found {len(expenses)} expenses for {user_id}")
            
            if expenses:
                print("💰 Expense details:")
                for i, expense in enumerate(expenses[:3], 1):  # Show first 3
                    print(f"  {i}. ${expense['amount']} - {expense['description']}")
                    print(f"     Date: {expense['date']}")
                    print(f"     Category: {expense['category']}")
                    print(f"     User ID in DB: {expense.get('user_id', 'N/A')}")
                    print()
                    
                if len(expenses) > 3:
                    print(f"  ... and {len(expenses) - 3} more expenses")
            else:
                print("   No expenses found")
                
        except Exception as e:
            print(f"❌ Error testing {user_id}: {str(e)}")
    
    print(f"\n📊 Summary:")
    print("If you see multiple expenses for different users, the filtering might not be working correctly.")
    print("If you only see expenses for the correct user, the filtering is working.")

if __name__ == "__main__":
    test_user_data() 