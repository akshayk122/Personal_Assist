# Agentinc Personal Assistant System

A comprehensive multi-agent personal assistant system using Agent Communication Protocol (ACP) servers that manages <!-- meetings, --> expenses, notes, health tracking, and diet management through specialized agents and a central orchestrator with intelligent user ID support and session memory.

## Quick Start with UV

```bash
# 1. Install uv (modern Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup the project
cd personal_assistant
uv sync

# 3. Configure environment
cp env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 4. (Optional) Set up Supabase for database storage
# See SUPABASE_SETUP.md for detailed instructions
# If you encounter "Database security policy violation" errors, see RLS_TROUBLESHOOTING.md

# 5. Start servers (3 separate terminals)
<!-- #make meeting      # Terminal 1: Meeting Manager (port 8100) -->
make expense      # Terminal 2: Expense Tracker (port 8200) 
make orchestrator # Terminal 3: Orchestrator (port 8300)

# 6. Launch Streamlit UI (4th terminal - optional)
make streamlit    # Terminal 4: Web UI (port 8501)

# 7. Test the system
uv run python -c "
import asyncio
from acp_sdk.client import Client

async def test():
    async with Client(base_url='http://localhost:8300') as client:
        response = await client.run_sync(
            agent='personal_assistant',
            input='What can you help me with?'
        )
        print(response.output[0].parts[0].content)

asyncio.run(test())
"
```

## Architecture Overview

The system consists of four main ACP servers with intelligent orchestration:

<!--
- **Server 1 (Port 8100)**: Meeting Manager Agent - Handles all meeting-related operations
-->
- **Server 2 (Port 8200)**: Expense Tracker Agent - Manages expense tracking and budget analysis  
- **Server 3 (Port 8300)**: Personal Assistant Orchestrator - Coordinates between all specialized agents
- **Server 4 (Port 8501)**: Streamlit Web UI - Modern web interface for user interaction

## Core Features

<!--
### 🗓️ Meeting Management
- **Smart Scheduling**: Schedule new meetings with automatic conflict detection
- **Flexible Queries**: List meetings by date range, status, or attendees
- **Advanced Search**: Search meetings by various criteria (title, attendees, location)
- **Meeting Updates**: Update meeting details, attendees, and status
- **Cancellation Support**: Cancel or delete meetings with confirmation
- **Conflict Detection**: Automatic checking for scheduling conflicts
- **User-Specific**: Support for multiple users with isolated meeting data
-->

### 💰 Expense Tracking
- **Intelligent Recording**: Record expenses with automatic categorization
- **Comprehensive Analytics**: Generate spending summaries and detailed analytics
- **Budget Management**: Track budgets with alerts and smart recommendations
- **Pattern Analysis**: Advanced spending pattern recognition and insights
- **Payment Methods**: Support for multiple payment methods (credit, cash, debit)
- **Category Organization**: Smart tagging and subcategory organization
- **User Isolation**: Multi-user support with data isolation
- **Flexible Filtering**: Filter expenses by date, category, payment method

### 📝 Notes Management
- **Smart Note Creation**: Create and organize personal and professional notes
- **Advanced Search**: Search notes by content, status, or creation date
- **Status Tracking**: Mark notes as completed, pending, or in-progress
- **Content Updates**: Update note content and status dynamically
- **Safe Deletion**: Delete notes with confirmation and backup
- **User-Specific**: Isolated note storage per user
- **Supabase Integration**: Persistent storage with database backup

### 🏃 Health and Diet Tracking
- **Goal Setting**: Set and track health goals (weight, calories, fitness targets)
- **Meal Logging**: Log daily meals with detailed calorie tracking
- **Progress Monitoring**: View progress towards health goals with visual indicators
- **Nutrition Analysis**: Track daily food intake with nutritional breakdown
- **Goal Management**: Update target values and current progress
- **Daily Totals**: Automatic calculation of daily calorie and nutrition totals
- **Health Insights**: Provide gentle guidance and encouragement
- **User-Specific**: Personal health data isolation per user

### 🧠 Intelligent Orchestration
- **Natural Language Processing**: Advanced query understanding and routing
- **Multi-Agent Coordination**: Seamless coordination between specialized agents
- **Context Awareness**: Intelligent routing based on query content
- **Session Memory**: Remembers conversation context within current session
- **User ID Support**: Automatic user identification and data isolation
- **Response Synthesis**: Combines results from multiple agents intelligently

### 🌐 Modern Web Interface
- **Streamlit UI**: Clean, responsive web interface
- **Real-time Chat**: Interactive chat interface with conversation history
- **Server Monitoring**: Real-time server status monitoring
- **Example Queries**: Quick action buttons for common tasks
- **Mobile Responsive**: Optimized for desktop and mobile devices
- **User-Friendly**: Intuitive design with clear navigation

### 👤 Multi-User Support
- **User ID Extraction**: Automatic user identification from queries
- **Pattern Recognition**: Supports various user ID patterns:
  - "for user: user123"
  - "user123's expenses"
  - "my expenses as user123"
  <!-- - "meetings for user123" -->
- **Data Isolation**: Complete user data separation and privacy
- **Session Memory**: User-specific conversation memory
- **Fallback Support**: Environment variable fallback for user ID

### 💾 Data Storage Options
- **JSON Storage**: Local file-based storage for development
- **Supabase Integration**: Cloud database with Row Level Security (RLS)
- **Automatic Backup**: Data persistence and recovery
- **User-Specific Tables**: Isolated data storage per user
- **Migration Support**: Easy transition between storage options

## Project Structure

```
personal_assistant/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── pyproject.toml              # Project configuration
├── env.example                  # Environment template
├── Makefile                    # Development commands
├── data/                        # JSON data storage
<!-- │   ├── meetings.json           # Meeting data (auto-generated) -->
│   ├── categories.json         # Categories config (auto-generated)
│   └── .gitkeep               # Git placeholder
├── servers/                     # ACP server implementations
<!-- │   ├── meeting_server.py       # Meeting Manager (Port 8100) -->
│   ├── expense_server.py       # Expense Tracker (Port 8200)
│   ├── orchestrator_server.py  # Orchestrator (Port 8300)
│   └── api_server.py           # API Server (Port 8400)
├── mcp_tools/                   # MCP tool implementations
<!-- │   ├── meeting_tools.py        # Meeting operations -->
│   ├── expense_tools.py        # Expense operations
│   ├── notes_tool.py           # Notes operations
│   └── health_diet_tools.py    # Health and diet operations
├── agents/                      # Agent implementations
│   ├── notes_agents.py         # Notes agent
│   └── health_diet_agent.py    # Health and diet agent
├── utils/                       # Utility modules
│   ├── gemini_config.py        # Gemini AI configuration
│   ├── supabase_config.py      # Supabase database configuration
│   └── data_manager.py         # JSON data operations
├── tests/                       # Test suite
<!-- │   ├── test_meetings.py -->
│   ├── test_expenses.py
│   └── test_orchestrator.py
├── SUPABASE_SETUP.md           # Supabase setup instructions
├── RLS_TROUBLESHOOTING.md      # RLS policy troubleshooting guide
├── USER_SPECIFIC_SETUP.md      # User-specific setup guide
├── database_setup.sql          # Database schema and RLS policies
<!-- ├── database_setup_user_specific.sql # User-specific database setup -->
├── streamlit_ui.py             # Streamlit web interface
├── run_streamlit.py            # Streamlit launcher
├── demo.py                     # System demonstration script
└── test_supabase_fix.py        # Test script for Supabase setup
```

## Setup Instructions

### 1. Environment Setup

```bash
# Clone or create the project directory
cd personal_assistant

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies using uv
uv sync

# Set up environment variables
cp env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

**Alternative installation methods:**
```bash
# Using pip to install uv
pip install uv

# Then sync dependencies
uv sync

# Or install specific dependency groups
uv sync --extra dev    # Install with development dependencies
uv sync --extra test   # Install with testing dependencies
```

### 2. Configure Environment

Edit your `.env` file:

```env
# Google AI API Key (Required)
GOOGLE_API_KEY=your_google_api_key_here

# Supabase Configuration (Optional)
SUPABASE_URL=your_supabase_url
SUPABASE_API_KEY=your_supabase_api_key
USER_ID=default_user

# Server Configuration (Default values)
<!-- MEETING_SERVER_PORT=8100 -->
EXPENSE_SERVER_PORT=8200
ORCHESTRATOR_SERVER_PORT=8300

# AI Model Configuration
MODEL_NAME=gemini/gemini-2.0-flash
MAX_TOKENS=1024
TEMPERATURE=0.7

# Data Configuration
DATA_PATH=./data
<!-- MEETINGS_FILE=meetings.json -->
EXPENSES_FILE=expenses.json
CATEGORIES_FILE=categories.json

# Logging
LOG_LEVEL=INFO
LOG_FILE=personal_assistant.log
```

### 3. Start the Servers

You need to run each server in a separate terminal:

```bash
<!-- # Terminal 1: Meeting Manager
cd personal_assistant
uv run python servers/meeting_server.py -->

# Terminal 2: Expense Tracker  
cd personal_assistant
uv run python servers/expense_server.py

# Terminal 3: Orchestrator
cd personal_assistant
uv run python servers/orchestrator_server.py
```

**Alternative using project scripts:**
```bash
<!-- # Terminal 1: Meeting Manager
uv run meeting-server -->

# Terminal 2: Expense Tracker
uv run expense-server

# Terminal 3: Orchestrator
uv run orchestrator-server
```

**Using Makefile commands:**
```bash
<!-- # Terminal 1: Meeting Manager
make meeting -->

# Terminal 2: Expense Tracker
make expense

# Terminal 3: Orchestrator
make orchestrator

# Terminal 4: Streamlit UI
make streamlit
```

## Usage Examples

### Using Streamlit Web UI (Recommended)

1. **Start all servers** (in separate terminals):
   ```bash
   <!-- make meeting      # Terminal 1 -->
   make expense      # Terminal 2  
   make orchestrator # Terminal 3
   ```

2. **Launch the web interface**:
   ```bash
   make streamlit    # Terminal 4
   ```

3. **Open your browser** to `http://localhost:8501`

4. **Start chatting!** Try these example queries:
   - "Schedule a team standup tomorrow at 9 AM"
   - "I spent $25 on lunch at Subway today"
   - "Add a note about the project meeting"
   - "Add a weight goal of 170 lbs"
   - "I ate oatmeal for breakfast, 320 calories"
   - "What did I eat today?"
   - "Show my expenses for user: john123"
   - "Schedule a meeting for user: alice456"

The web UI provides:
- Interactive chat interface with your personal assistant
- Real-time server status monitoring
- Example queries for quick actions  
- Mobile-friendly responsive design
- User-specific data isolation

### Using ACP SDK Client (Programmatic)

```python
import asyncio
from acp_sdk.client import Client

async def example_usage():
    # Query the orchestrator for complex requests
    async with Client(base_url="http://localhost:8300") as client:
        # Combined query
        response = await client.run_sync(
            agent="personal_assistant",
            input="What meetings do I have this week and how much did I spend on food?"
        )
        print(response.output[0].parts[0].content)
    
    # Query meeting manager directly
    async with Client(base_url="http://localhost:8100") as client:
        response = await client.run_sync(
            agent="meeting_manager",
            input="Schedule a team standup tomorrow at 9 AM"
        )
        print(response.output[0].parts[0].content)
    
    # Query expense tracker directly
    async with Client(base_url="http://localhost:8200") as client:
        response = await client.run_sync(
            agent="expense_tracker",
            input="I spent $25 on dinner at Italian restaurant"
        )
        print(response.output[0].parts[0].content)

# Run the example
asyncio.run(example_usage())

# Save as example.py and run with:
# uv run python example.py
```

### Example Queries

#### Meeting Management
- "Schedule a meeting with John tomorrow at 2 PM for project review"
- "Show me all meetings this week"
- "Find meetings with Sarah in the attendees"
- "Cancel the meeting with ID m001"
- "Check for conflicts on Friday at 3 PM"
- "Schedule a meeting for user: alice123"

#### Expense Tracking
- "I spent $12.50 on lunch at Subway today"
- "Show me all food expenses this month"
- "How much did I spend on transportation this quarter?"
- "Give me a budget analysis for entertainment"
- "What's my total spending this week?"
- "Show my expenses for user: john123"
- "I spent $45 on groceries for user: jane456"

#### Notes Management
- "Add a note about the client meeting tomorrow"
- "Show me all my notes"
- "Find notes about the project"
- "Mark note n001 as completed"
- "Delete the old meeting note"
- "Add a note for user: bob789"

#### Health and Diet Tracking
- "Add a weight goal of 170 lbs"
- "Update my weight goal to 165 lbs"
- "I ate oatmeal for breakfast, 320 calories"
- "What did I eat today?"
- "Show my health goals"
- "Log my lunch: chicken salad, 450 calories"
- "Add a weight goal for user: fitness_user"

#### Combined Queries (via Orchestrator)
- "What meetings do I have today and what did I spend yesterday?"
- "Show my schedule for next week and my food budget status"
- "Do I have any lunch meetings this week and what's my restaurant spending?"
- "Add a note about the meeting and log my lunch"
- "Show my expenses and health goals for user: user123"

#### User-Specific Queries
- "Show my expenses for user: john123"
- "Schedule a meeting for user: alice456"
- "Add a note for user: bob789"
- "I spent $30 on dinner for user: jane456"
- "What did I eat today for user: fitness_user"

## API Endpoints

### Meeting Manager (Port 8100)
- **POST** `/runs` - Agent: `meeting_manager`

### Expense Tracker (Port 8200)
- **POST** `/runs` - Agent: `expense_tracker`

### Orchestrator (Port 8300)
- **POST** `/runs` - Agent: `personal_assistant`

### API Server (Port 8400)
- **POST** `/query` - Handle user queries
- **GET** `/health` - Health check

### Streamlit UI (Port 8501)
- **Web Interface** - Interactive chat interface

## Data Storage

The system supports multiple storage options:

### JSON Storage (Default)
```json
// meetings.json
{
  "meeting_id": "uuid",
  "title": "Meeting Title",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "duration_minutes": 60,
  "attendees": ["email1@domain.com"],
  "location": "Conference Room A",
  "description": "Meeting description",
  "status": "scheduled|completed|cancelled",
  "user_id": "user123"
}

// categories.json
{
  "expense_categories": ["food", "transportation", "entertainment", "utilities", "healthcare", "shopping", "other"],
  "expense_subcategories": {
    "food": ["lunch", "dinner", "breakfast", "coffee", "snacks", "takeout", "groceries"],
    "transportation": ["gas", "parking", "public-transit", "rideshare", "car-maintenance"]
  },
  "payment_methods": ["cash", "credit", "debit", "online"],
  "meeting_types": ["team-standup", "client-meeting", "presentation", "interview", "training"],
  "meeting_locations": ["Conference Room A", "Conference Room B", "Virtual - Zoom", "Virtual - Google Meet"],
  "meeting_statuses": ["scheduled", "completed", "cancelled"]
}
```

### Supabase Database (Optional)

When configured, the system can use Supabase for persistent storage:

- **meetings** table: Meeting data with RLS policies
- **expenses** table: Expense data with RLS policies  
- **notes** table: Notes data with RLS policies
- **health_goals** table: Health goal tracking
- **food_logs** table: Daily food logging
- **users** table: User management and isolation

## Testing

```bash
# Install test dependencies
uv sync --extra test

# Run individual component tests
uv run pytest tests/test_meetings.py
uv run pytest tests/test_expenses.py
uv run pytest tests/test_orchestrator.py

# Run all tests
uv run pytest tests/

# Run tests with coverage
uv run pytest --cov=personal_assistant --cov-report=html

# Run only fast tests (exclude slow integration tests)
uv run pytest -m "not slow"

# Test Supabase integration
make test-supabase
```

## Development Commands

```bash
# Code quality
make format          # Format code
make lint            # Run linting
make test            # Run tests
make test-coverage   # Run tests with coverage

# Server management
make meeting         # Start meeting server
make expense         # Start expense server
make orchestrator    # Start orchestrator
make streamlit       # Start web UI
make servers         # Show server startup instructions

# Development workflow
make dev-setup       # Complete development setup
make check           # Quick development check
make check-full      # Full development check
make clean           # Clean cache and build files

# Demo and testing
make demo            # Run system demo
make test-supabase   # Test Supabase connection
```

## Advanced Features

### Session Memory
- **Conversation History**: Remembers previous interactions in current session
- **Context Awareness**: Understands references to previous actions
- **Pronoun Resolution**: Handles "it", "that", "the first one" based on context
- **User-Specific**: Each user has their own conversation memory

### User ID Support
- **Automatic Extraction**: Extracts user_id from various query patterns
- **Pattern Recognition**: Supports multiple user ID formats
- **Data Isolation**: Complete user data separation
- **Fallback Support**: Environment variable fallback
- **Privacy Protection**: User-specific data access controls

### Intelligent Routing
- **Query Analysis**: Automatically routes queries to appropriate agents
- **Multi-Agent Coordination**: Handles complex queries spanning multiple domains
- **Response Synthesis**: Combines results from multiple agents intelligently
- **Context Preservation**: Maintains context across agent interactions

### Health and Diet Features
- **Goal Tracking**: Set and monitor health goals with progress indicators
- **Meal Logging**: Detailed food intake tracking with calorie counting
- **Nutrition Analysis**: Comprehensive nutritional breakdown
- **Progress Visualization**: Visual progress indicators for goals
- **Gentle Guidance**: Supportive health recommendations

## Future Enhancements

### Integration Opportunities
- **Calendar Systems**: Google Calendar, Outlook integration
- **Banking APIs**: Automatic expense import from bank transactions
- **Communication**: Slack, Teams notifications for meetings
- **Voice Interface**: Speech-to-text for hands-free operation
- **Mobile App**: Dedicated mobile application
- **Wearable Integration**: Health data from smartwatches and fitness trackers

### Advanced Features
- **AI-Powered Insights**: Advanced spending pattern analysis and meeting optimization
- **Receipt Processing**: OCR for receipt scanning and automatic expense entry
- **Smart Scheduling**: AI-powered meeting time suggestions
- **Budget Automation**: Automatic budget adjustments based on spending patterns
- **Health Recommendations**: Personalized diet and exercise suggestions
- **Predictive Analytics**: Forecast spending and health trends

### Scalability
- **Database Integration**: PostgreSQL/MongoDB for larger datasets
- **Caching**: Redis for improved performance
- **Monitoring**: Comprehensive logging and metrics
- **Security**: Enhanced authentication and authorization
- **Microservices**: Containerized deployment with Docker
- **Cloud Deployment**: AWS, GCP, or Azure integration

## Troubleshooting

### Database Security Policy Violation

If you encounter the error "Database security policy violation":

1. **Quick Fix**: Run the RLS fix script in your Supabase SQL Editor:
   ```sql
   -- Copy and paste the contents of database_setup.sql
   ```

2. **Verify the fix**: Run the test script:
   ```bash
   uv run python test_supabase_fix.py
   ```

3. **Detailed instructions**: See `RLS_TROUBLESHOOTING.md` for comprehensive troubleshooting steps.

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8100
   
   # Kill the process or use different ports in .env
   ```

2. **Google API Key Issues**
   ```bash
   # Verify your API key is set
   echo $GOOGLE_API_KEY
   
   # Ensure it has Gemini API access enabled
   ```

3. **Module Import Errors**
   ```bash
   # Ensure you're in the right directory
   cd personal_assistant
   
   # Check Python path with uv
   uv run python -c "import sys; print(sys.path)"
   
   # Verify uv environment
   uv run python -c "import personal_assistant; print('Success!')"
   ```

4. **Data File Permissions**
   ```bash
   # Ensure data directory is writable
   chmod 755 data/
   ```

5. **Supabase Connection Issues**
   ```bash
   # Check environment variables
   echo $SUPABASE_URL
   echo $SUPABASE_API_KEY
   
   # Test Supabase connection
   uv run python test_supabase_fix.py
   ```

6. **User ID Issues**
   ```bash
   # Check user ID extraction
   uv run python -c "
   from servers.expense_server import extract_user_id_from_query
   print(extract_user_id_from_query('Show expenses for user: test123'))
   "
   ```

### Performance Tips

- Use the orchestrator for complex queries spanning multiple domains
- Query specialized agents directly for single-domain operations
- Monitor server logs for performance bottlenecks
- Consider increasing `max_tokens` for complex responses
- Use Supabase for better performance with large datasets
- Enable caching for frequently accessed data

## License

This project is created for educational and demonstration purposes following the ACP (Agent Communication Protocol) patterns.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review server logs for error details
3. Ensure all dependencies are correctly installed
4. Verify environment configuration
5. Test with the demo script: `make demo`

---

## Why UV?

This project uses [uv](https://github.com/astral-sh/uv) for dependency management, which provides:

- **Speed**: 10-100x faster than pip
- **Reliability**: Deterministic dependency resolution 
- **Simplicity**: Single tool for package management
- **Compatibility**: Drop-in replacement for pip/venv
- **Modern**: Built-in virtual environment management

### UV Commands Reference

```bash
# Basic usage
uv sync                    # Install dependencies
uv sync --extra dev        # Install with dev dependencies
uv run python script.py   # Run Python with project dependencies
uv add package            # Add new dependency
uv remove package         # Remove dependency

# Development workflow
make dev-setup            # Complete development setup
make test                 # Run tests
make format               # Format code
make lint                 # Check code quality
make servers              # Start all servers
```

**Built with UV, ACP SDK, CrewAI, Google Gemini AI, and Streamlit** 
