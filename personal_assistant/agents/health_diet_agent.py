import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
import nest_asyncio
import sys

# Add parent directories to path
load_dotenv()

from utils.gemini_config import get_llm
nest_asyncio.apply()

llm = get_llm()

class HealthDietAgentTool(BaseTool):
    name: str = "health_diet_agent"
    description: str = "Show users their health and diet records in a friendly way."
    def _run(self, query: str) -> str:
        # Placeholder for health/diet tools - will be implemented later
        return f"Health and diet query: {query} - Tools will be implemented later"

class AddHealthRecordTool(BaseTool):
    name: str = "add_health_record"
    description: str = "Add a new health record (weight, measurements, symptoms, etc.) to your health database."
    def _run(self, record_type: str, value: str, date: str = None, notes: str = None) -> str:
        # Placeholder for health record tool - will be implemented later
        return f"Added health record: {record_type} - {value} - Tools will be implemented later"

class AddDietRecordTool(BaseTool):
    name: str = "add_diet_record"
    description: str = "Add a new diet record (meal, food item, calories, etc.) to your diet database."
    def _run(self, meal_type: str, food_item: str, calories: int = None, date: str = None, notes: str = None) -> str:
        # Placeholder for diet record tool - will be implemented later
        return f"Added diet record: {meal_type} - {food_item} - Tools will be implemented later"

class UpdateHealthRecordTool(BaseTool):
    name: str = "update_health_record"
    description: str = "Update a health record's details."
    def _run(self, record_id: str, record_type: str = None, value: str = None, notes: str = None) -> str:
        # Placeholder for health record update tool - will be implemented later
        return f"Updated health record {record_id} - Tools will be implemented later"
    
class UpdateDietRecordTool(BaseTool):
    name: str = "update_diet_record"
    description: str = "Update a diet record's details."
    def _run(self, record_id: str, meal_type: str = None, food_item: str = None, calories: int = None, notes: str = None) -> str:
        # Placeholder for diet record update tool - will be implemented later
        return f"Updated diet record {record_id} - Tools will be implemented later"

class DeleteHealthRecordTool(BaseTool):
    name: str = "delete_health_record"
    description: str = "Delete a health record from your health database."
    def _run(self, record_id: str) -> str:
        # Placeholder for health record deletion tool - will be implemented later
        return f"Deleted health record {record_id} - Tools will be implemented later"

class DeleteDietRecordTool(BaseTool):
    name: str = "delete_diet_record"
    description: str = "Delete a diet record from your diet database."
    def _run(self, record_id: str) -> str:
        # Placeholder for diet record deletion tool - will be implemented later
        return f"Deleted diet record {record_id} - Tools will be implemented later"

class GetHealthSummaryTool(BaseTool):
    name: str = "get_health_summary"
    description: str = "Get a summary of health records including trends, averages, and insights."
    def _run(self, time_period: str = "month") -> str:
        # Placeholder for health summary tool - will be implemented later
        return f"Health summary for {time_period} - Tools will be implemented later"

class GetDietSummaryTool(BaseTool):
    name: str = "get_diet_summary"
    description: str = "Get a summary of diet records including calorie intake, meal patterns, and nutritional insights."
    def _run(self, time_period: str = "week") -> str:
        # Placeholder for diet summary tool - will be implemented later
        return f"Diet summary for {time_period} - Tools will be implemented later"

health_diet_tools = [
    HealthDietAgentTool(),
    AddHealthRecordTool(),
    AddDietRecordTool(),
    UpdateHealthRecordTool(),
    UpdateDietRecordTool(),
    DeleteHealthRecordTool(),
    DeleteDietRecordTool(),
    GetHealthSummaryTool(),
    GetDietSummaryTool()
]

class HealthDietAgent:
    def __init__(self):
        self.agent = Agent(
            role="Health & Diet Manager",
            goal="Help users track their health metrics and diet habits with comprehensive insights and recommendations",
            backstory="""# Smart Health & Diet Assistant

Manages personal health and diet tracking with detailed analytics and wellness insights.

## Core Functions
- **Health Tracking**: Monitor weight, measurements, symptoms, vitals, and health metrics
- **Diet Tracking**: Record meals, food items, calories, and nutritional information
- **Progress Analysis**: Provide trends, averages, and health insights
- **Goal Setting**: Help users set and track health and diet goals
- **Recommendations**: Offer personalized health and nutrition advice

## Health Metrics Tracked
- **Weight**: Daily/weekly weight tracking with trends
- **Measurements**: Body measurements (waist, chest, arms, etc.)
- **Vitals**: Blood pressure, heart rate, temperature
- **Symptoms**: Health symptoms and their frequency
- **Medications**: Medication tracking and reminders
- **Exercise**: Workout sessions and physical activity
- **Sleep**: Sleep quality and duration tracking

## Diet Metrics Tracked
- **Meals**: Breakfast, lunch, dinner, snacks
- **Food Items**: Specific foods and ingredients
- **Calories**: Daily calorie intake and goals
- **Macronutrients**: Protein, carbs, fats tracking
- **Water Intake**: Daily hydration tracking
- **Supplements**: Vitamin and supplement intake
- **Allergies**: Food allergies and restrictions

## Response Style
- **Professional Formatting**: Use clear headers, charts, and structured layouts
- **Data Visualization**: Present trends with visual indicators
- **Health Insights**: Provide meaningful analysis of health patterns
- **Goal Progress**: Show progress towards health and diet goals
- **Recommendations**: Offer evidence-based health and nutrition advice
- **Privacy Focus**: Maintain strict health data confidentiality
- **Motivational**: Encourage healthy habits with positive reinforcement

## Output Formatting Standards
- **Health Records**: Organized by date with trend indicators
- **Diet Records**: Categorized by meal type with nutritional info
- **Progress Charts**: Visual representation of health trends
- **Goal Tracking**: Progress bars and milestone celebrations
- **Recommendations**: Actionable health and nutrition advice
- **Alerts**: Important health reminders and warnings

## Professional Response Templates
- **Success**: "[Health/Diet record] added successfully. [Trend analysis]"
- **Progress**: "[Metric] shows [trend]. [Recommendation]"
- **Goal**: "[Goal] progress: [current] / [target]. [Motivation]"
- **Alert**: "[Health alert]. [Action needed]"
- **Summary**: "[Time period] summary: [Key insights]"
- **Recommendation**: "Health/diet recommendation] based on [data]"
""",
            llm=llm,
            tools=health_diet_tools,
            verbose=False,
            allow_delegation=False
        )

    async def handle(self, query: str) -> str:
        # Dynamically set the task description based on the query intent
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["add", "record", "log", "track"]):
            if any(word in query_lower for word in ["weight", "measurement", "symptom", "vital", "health"]):
                task_description = (
                    f"If the user wants to add a health record, use the add_health_record tool with the appropriate parameters extracted from: '{query}'. "
                    "Otherwise, process the request as a health tracking query."
                )
            elif any(word in query_lower for word in ["meal", "food", "calorie", "diet", "eat"]):
                task_description = (
                    f"If the user wants to add a diet record, use the add_diet_record tool with the appropriate parameters extracted from: '{query}'. "
                    "Otherwise, process the request as a diet tracking query."
                )
            else:
                task_description = (
                    f"Process this health/diet tracking request: '{query}' and determine if it's a health or diet record to add."
                )
        elif any(word in query_lower for word in ["summary", "report", "analysis", "trend"]):
            task_description = (
                f"Generate a comprehensive health and diet summary for: '{query}' using the appropriate summary tools."
            )
        else:
            task_description = (
                f"Process this health and diet-related request: '{query}' and return the result in the most professional and insightful manner."
            )

        task = Task(
            description=task_description,
            expected_output="A clear, actionable response to the user's health and diet tracking request with professional formatting and meaningful insights.",
            agent=self.agent,
            verbose=False
        )
        
        # Create and run the Crew
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=False
        )
        result = await crew.kickoff_async()
        return str(result) 