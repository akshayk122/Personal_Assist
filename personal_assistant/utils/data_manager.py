"""
Data Manager for JSON file operations
Handles reading and writing meetings and expenses data
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from pathlib import Path

class DataManager:
    """Manages JSON data files for meetings and expenses"""
    
    def __init__(self, data_path: str = "./data"):
        self.data_path = Path(data_path)
        self.data_path.mkdir(exist_ok=True)
        
        self.meetings_file = self.data_path / "meetings.json"
        self.expenses_file = self.data_path / "expenses.json"
        self.categories_file = self.data_path / "categories.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files with default data if they don't exist"""
        
        # Initialize meetings file
        if not self.meetings_file.exists():
            default_meetings = [
                {
                    "meeting_id": "m001",
                    "title": "Team Standup",
                    "date": "2024-01-15",
                    "time": "09:00",
                    "duration_minutes": 30,
                    "attendees": ["john@company.com", "sarah@company.com"],
                    "location": "Conference Room A",
                    "description": "Daily team sync",
                    "status": "scheduled",
                    "created_at": "2024-01-10T10:00:00Z",
                    "updated_at": "2024-01-10T10:00:00Z"
                },
                {
                    "meeting_id": "m002",
                    "title": "Client Presentation",
                    "date": "2024-01-16",
                    "time": "14:00",
                    "duration_minutes": 60,
                    "attendees": ["client@external.com"],
                    "location": "Virtual - Zoom",
                    "description": "Q4 results presentation",
                    "status": "scheduled",
                    "created_at": "2024-01-12T15:30:00Z",
                    "updated_at": "2024-01-12T15:30:00Z"
                }
            ]
            self._write_json(self.meetings_file, default_meetings)
        
        # Initialize expenses file
        if not self.expenses_file.exists():
            default_expenses = [
                {
                    "expense_id": "e001",
                    "amount": 12.50,
                    "currency": "USD",
                    "category": "food",
                    "subcategory": "lunch",
                    "description": "Subway sandwich",
                    "date": "2024-01-15",
                    "payment_method": "credit",
                    "is_recurring": False,
                    "tags": ["quick-meal"],
                    "created_at": "2024-01-15T12:30:00Z"
                },
                {
                    "expense_id": "e002",
                    "amount": 45.00,
                    "currency": "USD",
                    "category": "transportation",
                    "subcategory": "gas",
                    "description": "Shell gas station",
                    "date": "2024-01-14",
                    "payment_method": "debit",
                    "is_recurring": False,
                    "tags": ["car", "fuel"],
                    "created_at": "2024-01-14T18:45:00Z"
                }
            ]
            self._write_json(self.expenses_file, default_expenses)
        
        # Initialize categories file
        if not self.categories_file.exists():
            default_categories = {
                "expense_categories": [
                    "food", "transportation", "entertainment", 
                    "utilities", "healthcare", "shopping", "other"
                ],
                "meeting_types": [
                    "team-standup", "client-meeting", "presentation", 
                    "interview", "training", "one-on-one", "other"
                ]
            }
            self._write_json(self.categories_file, default_categories)
    
    def _read_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """Read JSON file and return data"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"Error reading {file_path}. File might be corrupted.")
            return []
    
    def _write_json(self, file_path: Path, data: List[Dict[str, Any]]):
        """Write data to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Meeting operations
    def get_meetings(self) -> List[Dict[str, Any]]:
        """Get all meetings"""
        return self._read_json(self.meetings_file)
    
    def add_meeting(self, meeting_data: Dict[str, Any]) -> str:
        """Add a new meeting and return the meeting ID"""
        meetings = self.get_meetings()
        
        # Generate UUID for meeting
        meeting_id = str(uuid.uuid4())
        
        # Add required fields
        meeting_data.update({
            "meeting_id": meeting_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })
        
        meetings.append(meeting_data)
        self._write_json(self.meetings_file, meetings)
        return meeting_id
    
    def update_meeting(self, meeting_id: str, updates: Dict[str, Any]) -> bool:
        """Update a meeting by ID"""
        meetings = self.get_meetings()
        
        for meeting in meetings:
            if meeting["meeting_id"] == meeting_id:
                meeting.update(updates)
                meeting["updated_at"] = datetime.now().isoformat()
                self._write_json(self.meetings_file, meetings)
                return True
        return False
    
    def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting by ID"""
        meetings = self.get_meetings()
        original_length = len(meetings)
        
        meetings = [m for m in meetings if m["meeting_id"] != meeting_id]
        
        if len(meetings) < original_length:
            self._write_json(self.meetings_file, meetings)
            return True
        return False
    
    # Expense operations
    def get_expenses(self) -> List[Dict[str, Any]]:
        """Get all expenses"""
        return self._read_json(self.expenses_file)
    
    def add_expense(self, expense_data: Dict[str, Any]) -> str:
        """Add a new expense and return the expense ID"""
        expenses = self.get_expenses()
        
        # Generate UUID for expense
        expense_id = str(uuid.uuid4())
        
        # Add required fields
        expense_data.update({
            "expense_id": expense_id,
            "created_at": datetime.now().isoformat()
        })
        
        expenses.append(expense_data)
        self._write_json(self.expenses_file, expenses)
        return expense_id
    
    def update_expense(self, expense_id: str, updates: Dict[str, Any]) -> bool:
        """Update an expense by ID"""
        expenses = self.get_expenses()
        
        for expense in expenses:
            if expense["expense_id"] == expense_id:
                expense.update(updates)
                self._write_json(self.expenses_file, expenses)
                return True
        return False
    
    def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense by ID"""
        expenses = self.get_expenses()
        original_length = len(expenses)
        
        expenses = [e for e in expenses if e["expense_id"] != expense_id]
        
        if len(expenses) < original_length:
            self._write_json(self.expenses_file, expenses)
            return True
        return False
    
    # Category operations
    def get_categories(self) -> Dict[str, List[str]]:
        """Get all categories"""
        return self._read_json(self.categories_file) 