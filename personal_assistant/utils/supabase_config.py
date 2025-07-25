"""
Supabase Configuration and Client Setup
Handles database connections for expense management
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
    """Manages Supabase client and database operations for expenses"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_API_KEY")
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

    
    def add_expense(self, expense_data: Dict[str, Any]) -> str:
        """Add a new expense to Supabase"""
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
                print(f"[Supabase] SUCCESS: Expense {expense_id} added to database")
                print(f"[Supabase] Response data: {result.data}")
                return expense_id
            else:
                print("[Supabase] ERROR: Insert returned no data")
                raise Exception("Failed to insert expense into Supabase")
                
        except Exception as e:
            logger.error(f"Error adding expense to Supabase: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
    
    def get_expenses(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get expenses from Supabase with optional filters"""
        if not self.is_connected():
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            query = self.client.table("expenses").select("*")
            
            # Apply filters if provided
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
            print(f"[Supabase] Query executed, checking results...")
            
            if result.data:
                count = len(result.data)
                print(f"[Supabase] Retrieved {count} expense(s)")
                if "category" in filters:
                    category = filters["category"].lower().strip()
                    matching = sum(1 for e in result.data if e["category"].lower().strip() == category)
                    print(f"[Supabase] {matching} expense(s) match category '{category}'")
                    # Print all unique categories found
                    unique_categories = set(e["category"].lower().strip() for e in result.data)
                    print(f"[Supabase] Categories found in results: {unique_categories}")
                return result.data
            else:
                print("[Supabase] No expenses found")
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
        expenses = self.get_expenses(filters)
        
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
    
    def get_notes(self,note_id:str) -> List[Dict[str, Any]]:
        """Get notes from Supabase"""
        if not self.is_connected():
            raise Exception("Supabase client not initialized. Check your credentials.")
        
        try:
            result = self.client.table("notes").select("*").execute()
            return result.data
        except Exception as e:
            logger.error(f"Error retrieving notes from Supabase: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

    def add_note(self, note_data: Dict[str, Any]) -> str:
        """Add a new note to Supabase"""
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
            logger.error(f"Error adding note to Supabase: {str(e)}")
            raise Exception(f"Database error: {str(e)}")

# Global instance
supabase_manager = SupabaseManager() 