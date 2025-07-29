"""
Simple Health and Diet Tools
Basic health goal tracking and food logging with Supabase integration
"""

from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, date
import uuid

from utils.supabase_config import supabase_manager

mcp = FastMCP()

# Fallback in-memory storage (if Supabase not available)
health_goals = {}
food_logs = []

@mcp.tool()
def add_health_goal(
    goal_type: str,
    target_value: float,
    description: str = None
) -> str:
    """Add a new health goal (weight, calories, etc.)"""
    try:
        # Try Supabase first
        if supabase_manager.is_connected():
            goal_data = {
                "goal_type": goal_type.lower(),
                "target_value": float(target_value),
                "current_value": 0.0,
                "description": description or "",
                "is_active": True
            }
            goal_id = supabase_manager.add_health_goal(goal_data)
            return f"✅ Health goal added!\n\n**Goal**: {goal_type.title()}\n**Target**: {target_value}\n**Goal ID**: {goal_id}"
        
        # Fallback to in-memory storage
        goal_id = str(uuid.uuid4())
        goal_data = {
            "goal_id": goal_id,
            "goal_type": goal_type.lower(),
            "target_value": target_value,
            "current_value": 0.0,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        health_goals[goal_id] = goal_data
        
        return f"✅ Health goal added! (Local Storage)\n\n**Goal**: {goal_type.title()}\n**Target**: {target_value}\n**Goal ID**: {goal_id}"
    
    except Exception as e:
        return f"❌ Error adding health goal: {str(e)}"

@mcp.tool()
def update_health_goal(
    goal_id: str,
    target_value: float = None,
    current_value: float = None,
    description: str = None
) -> str:
    """Update an existing health goal"""
    try:
        # Try Supabase first
        if supabase_manager.is_connected():
            updates = {}
            if target_value is not None:
                updates["target_value"] = float(target_value)
            if current_value is not None:
                updates["current_value"] = float(current_value)
            if description is not None:
                updates["description"] = description
            
            success = supabase_manager.update_health_goal(goal_id, updates)
            if success:
                return f"✅ Health goal updated!\n\n**Goal ID**: {goal_id}\n**Updates applied successfully**"
            else:
                return f"❌ Health goal {goal_id} not found or update failed"
        
        # Fallback to in-memory storage
        if goal_id not in health_goals:
            return f"❌ Health goal {goal_id} not found"
        
        goal = health_goals[goal_id]
        
        if target_value is not None:
            goal["target_value"] = target_value
        if current_value is not None:
            goal["current_value"] = current_value
        if description is not None:
            goal["description"] = description
        
        return f"✅ Health goal updated! (Local Storage)\n\n**Goal**: {goal['goal_type'].title()}\n**Target**: {goal['target_value']}\n**Current**: {goal['current_value']}"
    
    except Exception as e:
        return f"❌ Error updating health goal: {str(e)}"

@mcp.tool()
def get_health_goals() -> str:
    """Get all active health goals"""
    try:
        # Try Supabase first
        if supabase_manager.is_connected():
            goals = supabase_manager.get_health_goals()
            
            if not goals:
                return "📋 No active health goals found. Add a goal to get started!"
            
            result = "📋 **Active Health Goals**\n\n"
            for goal in goals:
                progress = (goal.get("current_value", 0) / goal["target_value"]) * 100 if goal["target_value"] > 0 else 0
                result += f"**{goal['goal_type'].title()}**\n"
                result += f"• Target: {goal['target_value']}\n"
                result += f"• Current: {goal.get('current_value', 0)}\n"
                result += f"• Progress: {progress:.1f}%\n"
                result += f"• Description: {goal.get('description', 'No description')}\n"
                result += f"• Goal ID: {goal['goal_id']}\n\n"
            
            return result
        
        # Fallback to in-memory storage
        active_goals = [goal for goal in health_goals.values() if goal.get("is_active", True)]
        
        if not active_goals:
            return "📋 No active health goals found. Add a goal to get started! (Local Storage)"
        
        result = "📋 **Active Health Goals** (Local Storage)\n\n"
        for goal in active_goals:
            progress = (goal.get("current_value", 0) / goal["target_value"]) * 100 if goal["target_value"] > 0 else 0
            result += f"**{goal['goal_type'].title()}**\n"
            result += f"• Target: {goal['target_value']}\n"
            result += f"• Current: {goal.get('current_value', 0)}\n"
            result += f"• Progress: {progress:.1f}%\n"
            result += f"• Description: {goal.get('description', 'No description')}\n"
            result += f"• Goal ID: {goal['goal_id']}\n\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error getting health goals: {str(e)}"

@mcp.tool()
def add_food_log(
    meal_type: str,
    food_item: str,
    calories: int = None
) -> str:
    """Add a food item to your daily log"""
    try:
        today = date.today().isoformat()
        
        # Try Supabase first
        if supabase_manager.is_connected():
            food_data = {
                "meal_type": meal_type.lower(),
                "food_item": food_item,
                "calories": calories,
                "date": today
            }
            food_id = supabase_manager.add_food_log(food_data)
            
            # Get today's total calories from Supabase
            today_foods = supabase_manager.get_food_logs(today)
            total_calories = sum(f.get("calories", 0) for f in today_foods)
            
            result = f"✅ Food logged!\n\n**Meal**: {meal_type.title()}\n**Food**: {food_item}\n"
            if calories:
                result += f"**Calories**: {calories}\n"
            result += f"\n📊 **Today's Total Calories**: {total_calories}"
            
            return result
        
        # Fallback to in-memory storage
        food_id = str(uuid.uuid4())
        
        food_data = {
            "food_id": food_id,
            "meal_type": meal_type.lower(),
            "food_item": food_item,
            "calories": calories,
            "date": today,
            "created_at": datetime.now().isoformat()
        }
        
        food_logs.append(food_data)
        
        # Calculate today's total calories
        today_foods = [f for f in food_logs if f["date"] == today]
        total_calories = sum(f.get("calories", 0) for f in today_foods)
        
        result = f"✅ Food logged! (Local Storage)\n\n**Meal**: {meal_type.title()}\n**Food**: {food_item}\n"
        if calories:
            result += f"**Calories**: {calories}\n"
        result += f"\n📊 **Today's Total Calories**: {total_calories}"
        
        return result
    
    except Exception as e:
        return f"❌ Error adding food log: {str(e)}"

@mcp.tool()
def get_food_log() -> str:
    """Get today's food log"""
    try:
        today = date.today().isoformat()
        
        # Try Supabase first
        if supabase_manager.is_connected():
            today_foods = supabase_manager.get_food_logs(today)
            
            if not today_foods:
                return "📋 No food logged today"
            
            # Group by meal type
            meals = {}
            for food in today_foods:
                meal_type = food["meal_type"]
                if meal_type not in meals:
                    meals[meal_type] = []
                meals[meal_type].append(food)
            
            result = "📋 **Today's Food Log**\n\n"
            total_calories = 0
            
            for meal_type, foods in meals.items():
                result += f"**{meal_type.title()}**\n"
                meal_calories = 0
                
                for food in foods:
                    result += f"• {food['food_item']}"
                    if food.get("calories"):
                        result += f" ({food['calories']} cal)"
                    result += "\n"
                    meal_calories += food.get("calories", 0)
                
                if meal_calories > 0:
                    result += f"  **Meal Total**: {meal_calories} calories\n"
                result += "\n"
                total_calories += meal_calories
            
            result += f"📊 **Daily Total**: {total_calories} calories"
            
            return result
        
        # Fallback to in-memory storage
        today_foods = [f for f in food_logs if f["date"] == today]
        
        if not today_foods:
            return "📋 No food logged today (Local Storage)"
        
        # Group by meal type
        meals = {}
        for food in today_foods:
            meal_type = food["meal_type"]
            if meal_type not in meals:
                meals[meal_type] = []
            meals[meal_type].append(food)
        
        result = "📋 **Today's Food Log** (Local Storage)\n\n"
        total_calories = 0
        
        for meal_type, foods in meals.items():
            result += f"**{meal_type.title()}**\n"
            meal_calories = 0
            
            for food in foods:
                result += f"• {food['food_item']}"
                if food.get("calories"):
                    result += f" ({food['calories']} cal)"
                result += "\n"
                meal_calories += food.get("calories", 0)
            
            if meal_calories > 0:
                result += f"  **Meal Total**: {meal_calories} calories\n"
            result += "\n"
            total_calories += meal_calories
        
        result += f"📊 **Daily Total**: {total_calories} calories"
        
        return result
    
    except Exception as e:
        return f"❌ Error getting food log: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio") 