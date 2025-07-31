"""
Supabase Configuration and Client Setup
Handles database connections for expense management with user_id support
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Manages Supabase client and database operations for expenses with user_id support"""
    
    def __init__(self, user_id: str = None):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_API_KEY")
        self.user_id = user_id or os.getenv("USER_ID", "default_user")
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the Supabase client"""
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not found in environment variables")
            logger.warning("Please set SUPABASE_URL and SUPABASE_API_KEY")
            return
        
        try:
            # Print URL for debugging (masking most of it)
            safe_url = self.supabase_url[:20] + "..." if self.supabase_url else "None"
            print(f"[Supabase] Initializing with URL: {safe_url}")
            
            # Ensure URL starts with https://
            if self.supabase_url and not self.supabase_url.startswith("https://"):
                self.supabase_url = "https://" + self.supabase_url
                print(f"[Supabase] Added https:// prefix to URL")
            
            self.client = create_client(self.supabase_url, self.supabase_key)
            print("[Supabase] Client initialized successfully")
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            print(f"[Supabase] Initialization error: {str(e)}")
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            self.client = None
    
    def is_connected(self) -> bool:
        """Check if Supabase client is available"""
        return self.client is not None

    # ============================================================================
    # EXPENSE METHODS WITH USER_ID SUPPORT
    # ============================================================================
    
    def add_expense(self, expense_data: Dict[str, Any]) -> str:
        """Add a new expense to Supabase with user_id"""
        print("[Supabase] Starting expense addition...")
        print(f"[Supabase] Expense data: {expense_data}")
        
        if not self.is_connected():
            print("[Supabase] ERROR: Client not initialized")
            print(f"[Supabase] URL Status: {'SET' if self.supabase_url else 'MISSING'}")
            print(f"[Supabase] API Key Status: {'SET' if self.supabase_key else 'MISSING'}")
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            # Generate UUID for expense
            expense_id = str(uuid.uuid4())
            
            # Prepare data for Supabase
            supabase_data = {
                "expense_id": expense_id,
                "user_id": self.user_id,  # Add user_id to expense data
                "amount": expense_data["amount"],
                "currency": expense_data.get("currency", "USD"),
                "category": expense_data["category"],
                "subcategory": expense_data.get("subcategory", ""),
                "description": expense_data["description"],
                "date": expense_data["date"],
                "payment_method": expense_data.get("payment_method", "credit"),
                "is_recurring": expense_data.get("is_recurring", False),
                "tags": expense_data.get("tags", []),
                "created_at": datetime.now().isoformat()
            }
            
            print("[Supabase] Attempting database insertion...")
            # Insert into Supabase
            result = self.client.table("expenses").insert(supabase_data).execute()
            
            if result.data:
                print(f"[Supabase] SUCCESS: Expense {expense_id} added to database for user: {self.user_id}")
                print(f"[Supabase] Response data: {result.data}")
                return expense_id
            else:
                print("[Supabase] ERROR: Insert returned no data")
                raise Exception("Failed to insert expense into Supabase")
                
        except Exception as e:
            error_msg = str(e)
            print(f"[Supabase] ERROR: {error_msg}")
            
            # Check for specific RLS policy violations
            if "security policy violation" in error_msg.lower() or "row level security" in error_msg.lower():
                print("[Supabase] RLS Policy Error Detected!")
                print("[Supabase] This indicates a Row Level Security policy issue.")
                print("[Supabase] Please check your Supabase RLS policies in the dashboard.")
                print("[Supabase] Run the database_setup_user_specific.sql script to fix RLS policies.")
                raise Exception("Database security policy violation. Please run database_setup_user_specific.sql in Supabase SQL Editor to fix RLS policies.")
            
            logger.error(f"Error adding expense to Supabase: {error_msg}")
            raise Exception(f"Database error: {error_msg}")
    
    def get_expenses(self, filters: Optional[Dict[str, Any]] = None, user_id: str = None) -> List[Dict[str, Any]]:
        """Get expenses from Supabase with optional filters and user_id filtering"""
        if not self.is_connected():
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            # Use provided user_id or default to instance user_id
            target_user_id = user_id or self.user_id
            
            query = self.client.table("expenses").select("*").eq("user_id", target_user_id)
            
            # Apply additional filters if provided
            if filters:
                print(f"[Supabase] Applying filters: {filters}")
                if "start_date" in filters:
                    query = query.gte("date", filters["start_date"])
                if "end_date" in filters:
                    query = query.lte("date", filters["end_date"])
                if "category" in filters:
                    category = filters["category"].lower().strip()  # Ensure lowercase and no whitespace
                    print(f"[Supabase] Filtering by category: '{category}'")
                    query = query.eq("category", category)
                if "min_amount" in filters:
                    query = query.gte("amount", filters["min_amount"])
                if "max_amount" in filters:
                    query = query.lte("amount", filters["max_amount"])
            
            # Order by date descending
            query = query.order("date", desc=True)
            
            result = query.execute()
            print(f"[Supabase] Query executed for user {target_user_id}, checking results...")
            
            # Check if result exists and has data
            if result is None:
                print(f"[Supabase] Query returned None result")
                return []
            
            if result.data is None:
                print(f"[Supabase] Query returned None data")
                return []
            
            if result.data:
                count = len(result.data)
                print(f"[Supabase] Retrieved {count} expense(s) for user {target_user_id}")
                if filters and "category" in filters:
                    category = filters["category"].lower().strip()
                    matching = sum(1 for e in result.data if e["category"].lower().strip() == category)
                    print(f"[Supabase] {matching} expense(s) match category '{category}'")
                    # Print all unique categories found
                    unique_categories = set(e["category"].lower().strip() for e in result.data)
                    print(f"[Supabase] Categories found in results: {unique_categories}")
                return result.data
            else:
                print(f"[Supabase] No expenses found for user {target_user_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving expenses from Supabase: {str(e)}")
            print(f"[Supabase] Error: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
    
    def update_expense(self, expense_id: str, updates: Dict[str, Any]) -> bool:
        """Update an expense in Supabase"""
        if not self.is_connected():
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            result = self.client.table("expenses").update(updates).eq("expense_id", expense_id).execute()
            
            if result.data:
                logger.info(f"Expense {expense_id} updated successfully in Supabase")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error updating expense in Supabase: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
    
    def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense from Supabase"""
        if not self.is_connected():
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            result = self.client.table("expenses").delete().eq("expense_id", expense_id).execute()
            
            if result.data:
                logger.info(f"Expense {expense_id} deleted successfully from Supabase")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error deleting expense from Supabase: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
    
    def get_expense_summary(self, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get expense summary and analytics from Supabase"""
        expenses = self.get_expenses(filters, user_id=self.user_id)
        
        if not expenses:
            return {
                "total_expenses": 0,
                "total_amount": 0.0,
                "categories": {},
                "average_expense": 0.0,
                "date_range": "No expenses found"
            }
        
        # Calculate summary statistics
        total_amount = sum(expense["amount"] for expense in expenses)
        total_expenses = len(expenses)
        
        # Category breakdown
        categories = {}
        for expense in expenses:
            category = expense["category"]
            if category not in categories:
                categories[category] = {"count": 0, "amount": 0.0}
            categories[category]["count"] += 1
            categories[category]["amount"] += expense["amount"]
        
        # Date range
        dates = [expense["date"] for expense in expenses]
        date_range = f"{min(dates)} to {max(dates)}" if dates else "No dates"
        
        return {
            "total_expenses": total_expenses,
            "total_amount": round(total_amount, 2),
            "categories": categories,
            "average_expense": round(total_amount / total_expenses, 2) if total_expenses > 0 else 0.0,
            "date_range": date_range
        }

    # ============================================================================
    # LEGACY METHODS (NO USER_ID SUPPORT) - FOR BACKWARD COMPATIBILITY
    # ============================================================================
    
    def get_notes(self,note_id:str) -> List[Dict[str, Any]]:
        """Get notes from Supabase (legacy - no user_id support)"""
        if not self.is_connected():
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            result = self.client.table("notes").select("*").execute()
            return result.data
        except Exception as e:
            logger.error(f"Error retrieving notes from Supabase: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def add_note(self, note_data: Dict[str, Any]) -> str:
        """Add a new note to Supabase (legacy - no user_id support)"""
        print("[Supabase] Starting note addition...")
        print(f"[Supabase] Note data: {note_data}")

        if not self.is_connected():
            print("[Supabase] ERROR: Client not initialized")
            print(f"[Supabase] URL Status: {'SET' if self.supabase_url else 'MISSING'}")
            print(f"[Supabase] API Key Status: {'SET' if self.supabase_key else 'MISSING'}")
            raise Exception("Supabase client not initialized. Check your credentials.")

        try:
            # Generate UUID for note
            note_id = str(uuid.uuid4())

            # Prepare data for Supabase
            supabase_data = {
                "note_id": note_id,
                "content": note_data["content"],
                "iscompleted": note_data.get("iscompleted", False),
                "created_at": datetime.now().isoformat()
            }

            print("[Supabase] Attempting note database insertion...")
            print(f"[Supabase] Inserting data: {supabase_data}")
            
            # Insert into Supabase
            result = self.client.table("notes").insert(supabase_data).execute()

            if result.data:
                print(f"[Supabase] SUCCESS: Note {note_id} added to database")
                print(f"[Supabase] Response data: {result.data}")
                return note_id
            else:
                print("[Supabase] ERROR: Insert returned no data")
                raise Exception("Failed to insert note into Supabase")

        except Exception as e:
            error_msg = str(e)
            print(f"[Supabase] ERROR: {error_msg}")
            
            # Check for specific RLS policy violations
            if "security policy violation" in error_msg.lower() or "row level security" in error_msg.lower():
                print("[Supabase] RLS Policy Error Detected!")
                print("[Supabase] This indicates a Row Level Security policy issue.")
                print("[Supabase] Please check your Supabase RLS policies in the dashboard.")
                print("[Supabase] Run the database_setup.sql script again to fix RLS policies.")
                raise Exception("Database security policy violation. Please run database_setup.sql in Supabase SQL Editor to fix RLS policies.")
            
            logger.error(f"Error adding note to Supabase: {error_msg}")
            raise Exception(f"Database error: {error_msg}")

    def update_note(self, note_id: str, updates: Dict[str, Any]) -> bool:
        """Update a note in Supabase (legacy - no user_id support)"""
        if not self.is_connected():
            raise Exception("Supabase client not initialized. Check your credentials.")
        try:
            result = self.client.table("notes").update(updates).eq("note_id", note_id).execute()
            if result.data:
                logger.info(f"Note {note_id} updated successfully in Supabase")
                return True
            else:
                logger.warning(f"No data returned when updating note {note_id}")
                return False
        except Exception as e:
            logger.error(f"Error updating note in Supabase: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def delete_note(self, note_id: str) -> bool:
        """Delete a note from Supabase (legacy - no user_id support)"""
        if not self.is_connected():
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            result = self.client.table("notes").delete().eq("note_id", note_id).execute()
            
            if result.data:
                logger.info(f"Note {note_id} deleted successfully from Supabase")
                return True
            else:
                logger.warning(f"No data returned when deleting note {note_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting note from Supabase: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    # Health Goals Methods (legacy - no user_id support)
    def add_health_goal(self, goal_data: Dict[str, Any]) -> str:
        """Add a new health goal to Supabase (legacy - no user_id support)"""
        print("[Supabase] Starting health goal addition...")
        print(f"[Supabase] Goal data: {goal_data}")
        
        if not self.is_connected():
            print("[Supabase] ERROR: Client not initialized")
            print(f"[Supabase] URL Status: {'SET' if self.supabase_url else 'MISSING'}")
            print(f"[Supabase] API Key Status: {'SET' if self.supabase_key else 'MISSING'}")
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            # Generate UUID for goal
            goal_id = str(uuid.uuid4())
            
            # Prepare data for Supabase
            supabase_data = {
                "goal_id": goal_id,
                "goal_type": goal_data["goal_type"],
                "target_value": goal_data["target_value"],
                "current_value": goal_data.get("current_value", 0.0),
                "description": goal_data.get("description", ""),
                "is_active": goal_data.get("is_active", True),
                "created_at": datetime.now().isoformat()
            }
            
            print("[Supabase] Attempting health goal database insertion...")
            # Insert into Supabase
            result = self.client.table("health_goals").insert(supabase_data).execute()
            
            if result.data:
                print(f"[Supabase] SUCCESS: Health goal {goal_id} added to database")
                print(f"[Supabase] Response data: {result.data}")
                return goal_id
            else:
                print("[Supabase] ERROR: Insert returned no data")
                raise Exception("Failed to insert health goal into Supabase")
                
        except Exception as e:
            error_msg = str(e)
            print(f"[Supabase] ERROR: {error_msg}")
            
            # Check for specific RLS policy violations
            if "security policy violation" in error_msg.lower() or "row level security" in error_msg.lower():
                print("[Supabase] RLS Policy Error Detected!")
                print("[Supabase] This indicates a Row Level Security policy issue.")
                print("[Supabase] Please check your Supabase RLS policies in the dashboard.")
                print("[Supabase] Run the database_setup.sql script again to fix RLS policies.")
                raise Exception("Database security policy violation. Please run database_setup.sql in Supabase SQL Editor to fix RLS policies.")
            
            logger.error(f"Error adding health goal to Supabase: {error_msg}")
            raise Exception(f"Database error: {error_msg}")

    def update_health_goal(self, goal_id: str, updates: Dict[str, Any]) -> bool:
        """Update a health goal in Supabase (legacy - no user_id support)"""
        if not self.is_connected():
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            result = self.client.table("health_goals").update(updates).eq("goal_id", goal_id).execute()
            
            if result.data:
                logger.info(f"Health goal {goal_id} updated successfully in Supabase")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error updating health goal in Supabase: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def get_health_goals(self) -> List[Dict[str, Any]]:
        """Get all health goals from Supabase (legacy - no user_id support)"""
        if not self.is_connected():
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            result = self.client.table("health_goals").select("*").eq("is_active", True).execute()
            return result.data if result.data else []
                
        except Exception as e:
            logger.error(f"Error retrieving health goals from Supabase: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    # Food Logging Methods (legacy - no user_id support)
    def add_food_log(self, food_data: Dict[str, Any]) -> str:
        """Add a new food log to Supabase (legacy - no user_id support)"""
        print("[Supabase] Starting food log addition...")
        print(f"[Supabase] Food data: {food_data}")
        
        if not self.is_connected():
            print("[Supabase] ERROR: Client not initialized")
            print(f"[Supabase] URL Status: {'SET' if self.supabase_url else 'MISSING'}")
            print(f"[Supabase] API Key Status: {'SET' if self.supabase_key else 'MISSING'}")
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            # Generate UUID for food log
            food_id = str(uuid.uuid4())
            
            # Prepare data for Supabase
            supabase_data = {
                "food_id": food_id,
                "meal_type": food_data["meal_type"],
                "food_item": food_data["food_item"],
                "calories": food_data.get("calories"),
                "date": food_data["date"],
                "created_at": datetime.now().isoformat()
            }
            
            print("[Supabase] Attempting food log database insertion...")
            # Insert into Supabase
            result = self.client.table("food_logs").insert(supabase_data).execute()
            
            if result.data:
                print(f"[Supabase] SUCCESS: Food log {food_id} added to database")
                print(f"[Supabase] Response data: {result.data}")
                return food_id
            else:
                print("[Supabase] ERROR: Insert returned no data")
                raise Exception("Failed to insert food log into Supabase")
                
        except Exception as e:
            error_msg = str(e)
            print(f"[Supabase] ERROR: {error_msg}")
            
            # Check for specific RLS policy violations
            if "security policy violation" in error_msg.lower() or "row level security" in error_msg.lower():
                print("[Supabase] RLS Policy Error Detected!")
                print("[Supabase] This indicates a Row Level Security policy issue.")
                print("[Supabase] Please check your Supabase RLS policies in the dashboard.")
                print("[Supabase] Run the database_setup.sql script again to fix RLS policies.")
                raise Exception("Database security policy violation. Please run database_setup.sql in Supabase SQL Editor to fix RLS policies.")
            
            logger.error(f"Error adding food log to Supabase: {error_msg}")
            raise Exception(f"Database error: {error_msg}")

    def get_food_logs(self, date: str = None) -> List[Dict[str, Any]]:
        """Get food logs from Supabase with optional date filter (legacy - no user_id support)"""
        if not self.is_connected():
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            query = self.client.table("food_logs").select("*")
            
            if date:
                query = query.eq("date", date)
            
            # Order by date descending, then by meal type
            query = query.order("date", desc=True).order("meal_type")
            
            result = query.execute()
            
            if result.data:
                return result.data
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving food logs from Supabase: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

# Global instance for backward compatibility
supabase_manager = SupabaseManager() 