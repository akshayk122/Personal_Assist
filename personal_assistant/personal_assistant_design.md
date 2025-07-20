# Personal Assistant System Design

## Project Overview
A multi-agent personal assistant system using Agent Communication Protocol (ACP) servers that manages meetings and expenses through specialized agents and a central orchestrator.

## System Architecture

### Core Components
- **ACP Server 1**: Meeting Manager Agent (Port 8100)
- **ACP Server 2**: Expense Tracker Agent (Port 8200) 
- **ACP Server 3**: Personal Assistant Orchestrator (Port 8300)

### Technology Stack
- **Framework**: ACP SDK with FastMCP for server communication
- **AI Model**: Google Gemini 2.0 Flash
- **Tools**: MCP (Model Context Protocol) for data management
- **Data Storage**: JSON files (dummy data initially)
- **Language**: Python 3.11+

## Agent Specifications

### 1. Meeting Manager Agent (Server 1)
**Purpose**: Track, schedule, and manage all meeting-related activities

**Features**:
- Add new meetings with details (title, date, time, attendees, location)
- List upcoming meetings by date range
- Search meetings by title, attendee, or date
- Update meeting details
- Delete/cancel meetings
- Get meeting reminders and conflicts

**MCP Tools**:
- `add_meeting(title, date, time, duration, attendees, location, description)`
- `list_meetings(start_date, end_date, status)`
- `search_meetings(query, search_type)`
- `update_meeting(meeting_id, updates)`
- `delete_meeting(meeting_id)`
- `get_meeting_conflicts(date, time, duration)`

**Data Structure**:
```json
{
  "meeting_id": "uuid",
  "title": "string",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "duration_minutes": "integer",
  "attendees": ["email1", "email2"],
  "location": "string",
  "description": "string",
  "status": "scheduled|completed|cancelled",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### 2. Expense Tracker Agent (Server 2)
**Purpose**: Monitor, categorize, and analyze personal expenses

**Features**:
- Record new expenses with categories
- List expenses by date range, category, or amount
- Calculate spending summaries and budgets
- Generate expense reports
- Track recurring expenses
- Categorize expenses automatically

**MCP Tools**:
- `add_expense(amount, category, description, date, payment_method)`
- `list_expenses(start_date, end_date, category, min_amount, max_amount)`
- `get_expense_summary(period, group_by)`
- `update_expense(expense_id, updates)`
- `delete_expense(expense_id)`
- `get_budget_status(category, period)`

**Data Structure**:
```json
{
  "expense_id": "uuid",
  "amount": "float",
  "currency": "USD",
  "category": "food|transportation|entertainment|utilities|healthcare|other",
  "subcategory": "string",
  "description": "string",
  "date": "YYYY-MM-DD",
  "payment_method": "cash|credit|debit|online",
  "is_recurring": "boolean",
  "tags": ["tag1", "tag2"],
  "created_at": "timestamp"
}
```

### 3. Personal Assistant Orchestrator (Server 3)
**Purpose**: Central hub that coordinates between meeting and expense agents

**Features**:
- Natural language query processing
- Route requests to appropriate specialized agents
- Combine data from multiple agents for comprehensive responses
- Provide unified interface for all personal assistant functions
- Handle complex queries requiring multiple agent interactions

**Capabilities**:
- "Show me my meetings for tomorrow and yesterday's expenses"
- "Did I spend more on food this month than last month?"
- "Do I have any meetings during lunch time this week?"
- "What's my total spending for this quarter and upcoming important meetings?"

## File Structure
```
personal_assistant/
├── README.md
├── requirements.txt
├── .env.example
├── data/
│   ├── meetings.json
│   ├── expenses.json
│   └── categories.json
├── servers/
│   ├── meeting_server.py      # ACP Server 1 (Port 8100)
│   ├── expense_server.py      # ACP Server 2 (Port 8200)
│   └── orchestrator_server.py # ACP Server 3 (Port 8300)
├── mcp_tools/
│   ├── meeting_tools.py       # MCP tools for meetings
│   └── expense_tools.py       # MCP tools for expenses
├── utils/
│   ├── gemini_config.py       # Gemini model configuration
│   ├── data_manager.py        # JSON data operations
│   └── validators.py          # Input validation
└── tests/
    ├── test_meetings.py
    ├── test_expenses.py
    └── test_orchestrator.py
```

## Configuration Pattern (Following Your Setup)

### Gemini Model Configuration
```python
import os
from crewai import LLM

# Environment setup
os.environ["GOOGLE_API_KEY"] = "your-api-key"

# LLM configuration
llm = LLM(model="gemini/gemini-2.0-flash", max_tokens=1024)

# Config for RAG tools
config = {
    "llm": {
        "provider": "google",
        "config": {
            "model": "gemini/gemini-2.0-flash",
        }
    },
    "embedding_model": {
        "provider": "google",
        "config": {
            "model": "models/embedding-001"
        }
    }
}
```

### ACP Server Pattern
```python
from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Server, RunYield, RunYieldResume
from crewai import Agent, Task, Crew, LLM
import nest_asyncio

nest_asyncio.apply()
server = Server()
llm = LLM(model="gemini/gemini-2.0-flash", max_tokens=1000)

@server.agent(name="agent_name")
async def agent(input: list[Message]) -> AsyncGenerator[RunYield, RunYieldResume]:
    # Agent implementation
    pass

if __name__ == "__main__":
    server.run(port=PORT_NUMBER)
```

## Dummy Data Examples

### Sample Meetings Data
```json
[
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
    "created_at": "2024-01-10T10:00:00Z"
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
    "created_at": "2024-01-12T15:30:00Z"
  }
]
```

### Sample Expenses Data
```json
[
  {
    "expense_id": "e001",
    "amount": 12.50,
    "currency": "USD",
    "category": "food",
    "subcategory": "lunch",
    "description": "Subway sandwich",
    "date": "2024-01-15",
    "payment_method": "credit",
    "is_recurring": false,
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
    "is_recurring": false,
    "tags": ["car", "fuel"],
    "created_at": "2024-01-14T18:45:00Z"
  }
]
```

## Implementation Steps

### Phase 1: Setup & Infrastructure
1. Create project folder structure
2. Setup environment and dependencies
3. Create dummy data files
4. Implement basic data management utilities

### Phase 2: Individual Agents
1. Implement Meeting Manager Agent (Server 1)
2. Implement Expense Tracker Agent (Server 2)
3. Test individual agent functionality

### Phase 3: Integration
1. Implement Personal Assistant Orchestrator (Server 3)
2. Create inter-agent communication
3. Test multi-agent workflows

### Phase 4: Enhancement
1. Add advanced query processing
2. Implement data persistence improvements
3. Add validation and error handling
4. Create comprehensive test suite

## Usage Examples

### Meeting Management
```python
# Client request to Meeting Server
await client.run_sync(
    agent="meeting_manager", 
    input="Schedule a meeting with John tomorrow at 2 PM for project review"
)
```

### Expense Tracking
```python
# Client request to Expense Server
await client.run_sync(
    agent="expense_tracker", 
    input="I spent $25 on dinner at Italian restaurant last night"
)
```

### Orchestrated Queries
```python
# Client request to Orchestrator
await client.run_sync(
    agent="personal_assistant", 
    input="What meetings do I have this week and how much did I spend on food?"
)
```

## Future Enhancements
- Integration with real calendar systems (Google Calendar, Outlook)
- Connection to banking APIs for automatic expense tracking
- Mobile app interface
- Voice command support
- AI-powered expense categorization
- Budget alerts and recommendations
- Meeting transcription and summary
- Expense receipt scanning and OCR

## Success Metrics
- Successful agent communication and data exchange
- Accurate query processing and response generation
- Proper data persistence and retrieval
- Error handling and graceful degradation
- Performance benchmarks (response time < 2 seconds) 