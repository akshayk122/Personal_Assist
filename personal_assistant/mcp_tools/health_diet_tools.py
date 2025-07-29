"""
Simple Health and Diet Tools
Basic health goal tracking and food logging
"""

from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, date
import uuid

mcp = FastMCP()

# Simple in-memory storage
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
        
        return f"✅ Health goal added!\n\n**Goal**: {goal_type.title()}\n**Target**: {target_value}\n**Goal ID**: {goal_id}"
    
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
        if goal_id not in health_goals:
            return f"❌ Health goal {goal_id} not found"
        
        goal = health_goals[goal_id]
        
        if target_value is not None:
            goal["target_value"] = target_value
        if current_value is not None:
            goal["current_value"] = current_value
        if description is not None:
            goal["description"] = description
        
        return f"✅ Health goal updated!\n\n**Goal**: {goal['goal_type'].title()}\n**Target**: {goal['target_value']}\n**Current**: {goal['current_value']}"
    
    except Exception as e:
        return f"❌ Error updating health goal: {str(e)}"

@mcp.tool()
def add_food_log(
    meal_type: str,
    food_item: str,
    calories: int = None
) -> str:
    """Add a food item to your daily log"""
    try:
        food_id = str(uuid.uuid4())
        today = date.today().isoformat()
        
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
        
        result = f"✅ Food logged!\n\n**Meal**: {meal_type.title()}\n**Food**: {food_item}\n"
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
        today_foods = [f for f in food_logs if f["date"] == today]
        
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
    
    except Exception as e:
        return f"❌ Error getting food log: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio") 