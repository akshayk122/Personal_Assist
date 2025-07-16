"""
ACP Server 3 - Personal Assistant Orchestrator 
Port: 8300

Coordinates between Meeting Manager and Expense Tracker agents
Following the pattern from acp_demo.py
"""

from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Server, RunYield, RunYieldResume
from acp_sdk.client import Client
from crewai import Agent, Task, Crew
import nest_asyncio
import sys
import os
import asyncio

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.gemini_config import get_llm

# Apply asyncio patch for Jupyter compatibility
nest_asyncio.apply()

# Initialize server and get configured LLM
server = Server()
llm = get_llm()

class SubAgentCommunicator:
    """Handles communication with meeting and expense servers"""
    
    def __init__(self):
        self.meeting_server_url = "http://localhost:8100"
        self.expense_server_url = "http://localhost:8200"
    
    async def query_meeting_agent(self, query: str) -> str:
        """Query the meeting management agent"""
        try:
            async with Client(base_url=self.meeting_server_url) as client:
                run = await client.run_sync(
                    agent="meeting_manager", 
                    input=query
                )
                return run.output[0].parts[0].content
        except Exception as e:
            return f"Unable to contact Meeting Manager: {str(e)}"
    
    async def query_expense_agent(self, query: str) -> str:
        """Query the expense tracking agent"""
        try:
            async with Client(base_url=self.expense_server_url) as client:
                run = await client.run_sync(
                    agent="expense_tracker", 
                    input=query
                )
                return run.output[0].parts[0].content
        except Exception as e:
            return f"Unable to contact Expense Tracker: {str(e)}"

# Initialize communicator
sub_agent_comm = SubAgentCommunicator()

@server.agent(name="personal_assistant")
async def orchestrator_agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    """
    Personal Assistant Orchestrator Agent
    
    Acts as the central hub that:
    - Analyzes user queries to determine which specialized agents to consult
    - Coordinates between meeting and expense management agents
    - Combines results from multiple agents for comprehensive responses
    - Handles complex queries requiring multiple agent interactions
    """
    
    try:
        # Extract user query
        user_query = input[0].parts[0].content
        
        # Create orchestrator agent
        orchestrator = Agent(
            role="Personal Assistant Orchestrator",
            goal="Intelligently coordinate between specialized agents to provide comprehensive personal assistance",
            backstory="""You are an intelligent personal assistant coordinator with expertise in 
            understanding user needs and efficiently routing requests to specialized services. You excel at:
            - Analyzing user queries to identify meeting-related, expense-related, or combined needs
            - Coordinating between multiple specialized agents (Meeting Manager and Expense Tracker)
            - Synthesizing information from different sources into coherent, actionable responses
            - Handling complex requests that span multiple domains (meetings and expenses)
            - Providing proactive suggestions and insights based on combined data
            
            You have access to two specialized agents:
            1. Meeting Manager: Handles all meeting-related operations (scheduling, conflicts, etc.)
            2. Expense Tracker: Handles all expense-related operations (tracking, budgets, etc.)
            
            You can query these agents individually or in combination to provide comprehensive assistance.""",
            verbose=True,
            allow_delegation=False,
            llm=llm,
            max_retry_limit=3
        )
        
        # Create orchestration task
        orchestration_task = Task(
            description=f"""
            Analyze this user request and coordinate appropriate responses: "{user_query}"
            
            Your responsibilities:
            1. ANALYZE the query to determine if it relates to:
               - Meetings only (schedule, conflicts, attendees, etc.)
               - Expenses only (spending, budgets, categories, etc.)
               - Both meetings and expenses (combined queries)
               - General personal assistant tasks
            
            2. DETERMINE the appropriate agent(s) to consult:
               - Meeting-related queries → Meeting Manager Agent
               - Expense-related queries → Expense Tracker Agent  
               - Combined queries → Both agents
               - General queries → Provide general assistance
            
            3. COORDINATE responses from multiple agents if needed and synthesize them into a 
               coherent, comprehensive response.
            
            4. PROVIDE additional context, insights, or suggestions that add value beyond 
               individual agent responses.
            
            Examples of query types:
            - "Schedule a meeting with John tomorrow" → Meeting Manager only
            - "How much did I spend on food this month?" → Expense Tracker only
            - "Do I have any meetings during lunch time and what did I spend on lunch yesterday?" → Both agents
            - "What's my schedule and spending summary for this week?" → Both agents
            
            Always aim to provide the most helpful and complete response possible.
            """,
            expected_output="""
            A comprehensive response that addresses the user's request by:
            - Clearly identifying what type of assistance was requested
            - Coordinating with appropriate specialized agents as needed
            - Providing integrated results from multiple agents when applicable
            - Adding contextual insights and proactive suggestions
            - Ensuring the response is coherent and actionable
            - Offering next steps or related assistance when appropriate
            """,
            agent=orchestrator,
            verbose=True,
            max_retry_limit=3
        )
        
        # Execute the orchestration task
        crew = Crew(
            agents=[orchestrator],
            tasks=[orchestration_task],
            verbose=True
        )
        
        # Get the AI analysis first
        analysis_result = await crew.kickoff_async()
        
        # Now determine which agents to query based on keywords and context
        query_lower = user_query.lower()
        
        needs_meeting_agent = any(keyword in query_lower for keyword in [
            'meeting', 'schedule', 'calendar', 'appointment', 'conflict', 
            'attendee', 'reschedule', 'cancel', 'book', 'available'
        ])
        
        needs_expense_agent = any(keyword in query_lower for keyword in [
            'expense', 'spend', 'spent', 'cost', 'money', 'budget', 'pay', 
            'paid', 'purchase', 'buy', 'bought', 'price', 'dollar', '$'
        ])
        
        # Query appropriate agents
        agent_responses = []
        
        if needs_meeting_agent:
            meeting_response = await sub_agent_comm.query_meeting_agent(user_query)
            agent_responses.append(("🕐 Meeting Manager", meeting_response))
        
        if needs_expense_agent:
            expense_response = await sub_agent_comm.query_expense_agent(user_query)
            agent_responses.append(("💰 Expense Tracker", expense_response))
        
        # Compile comprehensive response
        if agent_responses:
            response = f"""**Personal Assistant Orchestrator**

**Query Analysis:** {str(analysis_result)}

---

"""
            # Add responses from specialized agents
            for agent_name, agent_response in agent_responses:
                response += f"""## {agent_name} Response:

{agent_response}

---

"""
            
            response += """
🔗 **Integrated Summary:**
The above responses from specialized agents have been coordinated to provide comprehensive assistance. Each agent focuses on its area of expertise while I ensure the overall coherence and completeness of the response.

**Next Steps:**
- For meeting operations: Contact the Meeting Manager directly
- For expense operations: Contact the Expense Tracker directly  
- For complex queries: Continue using this orchestrator for coordinated responses

**Tip:** You can ask questions that span both domains, like "What meetings do I have this week and how much did I spend on client dinners?" for integrated insights.
"""
        else:
            # General query not requiring specialized agents
            response = f"""🤖 **Personal Assistant Orchestrator**

**Analysis:** {str(analysis_result)}

---

**Available Services:**
I coordinate between two specialized agents to help you:

**Meeting Management:**
- Schedule and manage meetings
- Check for conflicts  
- Update meeting details
- Search meetings by various criteria

**Expense Tracking:**
- Record and categorize expenses
- Generate spending summaries
- Analyze budgets and spending patterns
- Track expenses across time periods

**Integrated Assistance:**
- Combine meeting and expense information
- Provide comprehensive personal assistance
- Coordinate complex multi-domain queries

**How to Use:**
- Ask meeting questions like: "Schedule a team standup tomorrow at 9 AM"
- Ask expense questions like: "How much did I spend on food this month?"
- Ask combined questions like: "What meetings do I have and what's my spending this week?"
"""
        
        yield Message(parts=[MessagePart(content=response)])
        
    except Exception as e:
        error_response = f"Error in Personal Assistant Orchestrator: {str(e)}"
        yield Message(parts=[MessagePart(content=error_response)])

if __name__ == "__main__":
    print(" Starting Personal Assistant Orchestrator on port 8300...")
    print("Available endpoints:")
    print("  - POST /runs (agent: personal_assistant)")
    print("Coordinates between:")
    print("  - Meeting Manager (port 8100)")
    print("  - Expense Tracker (port 8200)")
    print("\n Example queries:")
    print(" 'Schedule a meeting with John tomorrow at 2 PM'")
    print("'I spent $25 on lunch today'") 
    print("'What meetings do I have this week and my food expenses?'")
    
    server.run(port=8300) 