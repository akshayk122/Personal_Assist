# 🚀 Personal Assistant Quick Start Guide

Get your Personal Assistant system up and running in minutes!

## 📋 Prerequisites

- **Python 3.11+** installed
- **UV package manager** (recommended) or pip
- **Google API Key** for Gemini model

## ⚡ Fast Setup (3 minutes)

### 1. Install UV (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Setup Project
```bash
cd personal_assistant
uv sync
```

### 3. Configure Environment
```bash
cp env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### 4. Start All Servers
You need **4 separate terminals**:

**Terminal 1 - Meeting Manager:**
```bash
make meeting
```

**Terminal 2 - Expense Tracker:**
```bash
make expense
```

**Terminal 3 - Orchestrator:**
```bash
make orchestrator
```

**Terminal 4 - Web UI:**
```bash
make streamlit
```

### 5. Open Web Interface
- Navigate to: **http://localhost:8501**
- Start chatting with your personal assistant!

## 🧪 Test the System

Run the demo script to verify everything works:
```bash
make demo
```

## 💬 Example Queries

Try these in the web interface:

### Meeting Management
- "Schedule a team standup tomorrow at 9 AM"
- "Show me all meetings this week"
- "Check for conflicts on Friday at 3 PM"

### Expense Tracking
- "I spent $25 on lunch at Subway today"
- "Show me all food expenses this month"
- "How much did I spend on transportation?"

### Combined Queries
- "What meetings do I have today and what did I spend yesterday?"
- "Show my schedule for next week and my food budget status"

## 🔧 Troubleshooting

### Servers Not Starting?
1. Check if ports are available (8100, 8200, 8300, 8501)
2. Verify your Google API key is set correctly
3. Run `uv sync` to ensure dependencies are installed

### Can't Connect to Servers?
- Ensure all three ACP servers are running before starting the UI
- Check the server status in the Streamlit sidebar
- Look for error messages in the terminal outputs

### Getting AI Errors?
- Verify your `GOOGLE_API_KEY` is valid and has Gemini access
- Check your internet connection
- Ensure you have sufficient API quota

## 🎯 Quick Commands Reference

| Command | Purpose |
|---------|---------|
| `make meeting` | Start Meeting Manager (port 8100) |
| `make expense` | Start Expense Tracker (port 8200) |
| `make orchestrator` | Start Orchestrator (port 8300) |
| `make streamlit` | Start Web UI (port 8501) |
| `make demo` | Run system test |
| `make install` | Install dependencies |
| `make test` | Run tests |

## 🌟 What's Next?

1. **Explore the Web UI** - Try different types of queries
2. **Check the API** - Use the SDK client for programmatic access
3. **Customize** - Modify the agents for your specific needs
4. **Extend** - Add new MCP tools and capabilities

## 📚 Learn More

- **README.md** - Full documentation
- **API Examples** - Programmatic usage with ACP SDK
- **MCP Tools** - Extend functionality with custom tools
- **Architecture** - Understand the multi-agent system

## 🆘 Need Help?

- Check the full README.md for detailed documentation
- Review the example code in the repository
- Look at the MCP tools implementation for reference

---

**🎉 Happy Personal Assisting!** 