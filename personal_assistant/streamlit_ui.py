"""
Streamlit UI for Personal Assistant System
Provides a web interface to interact with the orchestrator server
"""

import streamlit as st
import asyncio
import time
from datetime import datetime
from acp_sdk.client import Client
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure Streamlit page
st.set_page_config(
    page_title="Personal Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'server_status' not in st.session_state:
    st.session_state.server_status = {
        'orchestrator': 'unknown',
        'meeting': 'unknown', 
        'expense': 'unknown'
    }
if 'user_input' not in st.session_state:
    st.session_state.user_input = ''
if 'clear_input' not in st.session_state:
    st.session_state.clear_input = False

async def check_server_status(url: str) -> bool:
    """Check if a server is running"""
    try:
        async with Client(base_url=url) as client:
            # Simple health check by attempting to connect
            return True
    except Exception:
        return False

async def send_query_to_orchestrator(query: str) -> str:
    """Send query to the orchestrator server"""
    try:
        async with Client(base_url="http://localhost:8300") as client:
            run = await client.run_sync(
                agent="personal_assistant",
                input=query
            )
            return run.output[0].parts[0].content
    except Exception as e:
        return f"❌ Error connecting to Personal Assistant: {str(e)}\n\nPlease ensure the orchestrator server is running on port 8300."

async def check_all_servers():
    """Check status of all servers"""
    servers = {
        'orchestrator': 'http://localhost:8300',
        'meeting': 'http://localhost:8100',
        'expense': 'http://localhost:8200'
    }
    
    status = {}
    for name, url in servers.items():
        status[name] = await check_server_status(url)
    
    return status

def display_server_status():
    """Display server status in sidebar"""
    st.sidebar.markdown("## 🔧 Server Status")
    
    # Check server status
    if st.sidebar.button("🔄 Refresh Status"):
        with st.spinner("Checking servers..."):
            status = asyncio.run(check_all_servers())
            st.session_state.server_status = status
    
    # Display status
    servers = {
        'Orchestrator (8300)': st.session_state.server_status.get('orchestrator', False),
        'Meeting Manager (8100)': st.session_state.server_status.get('meeting', False),
        'Expense Tracker (8200)': st.session_state.server_status.get('expense', False)
    }
    
    for server_name, is_running in servers.items():
        if is_running:
            st.sidebar.success(f"✅ {server_name}")
        else:
            st.sidebar.error(f"❌ {server_name}")

def display_example_queries():
    """Display example queries in sidebar"""
    st.sidebar.markdown("## 💡 Example Queries")
    
    examples = {
        "🕐 Meeting Management": [
            "Schedule a team standup tomorrow at 9 AM",
            "Show me all meetings this week",
            "Find meetings with John in the title",
            "Check for conflicts on Friday at 3 PM"
        ],
        "💰 Expense Tracking": [
            "I spent $25 on lunch at Subway today",
            "Show me all food expenses this month", 
            "How much did I spend on transportation?",
            "Give me a budget analysis for entertainment"
        ],
        "🔗 Combined Queries": [
            "What meetings do I have today and what did I spend yesterday?",
            "Show my schedule for next week and my food budget status",
            "Do I have lunch meetings this week and restaurant expenses?"
        ]
    }
    
    for category, queries in examples.items():
        with st.sidebar.expander(category):
            for query in queries:
                if st.button(f"📝 {query}", key=f"example_{query[:20]}"):
                    st.session_state.current_query = query

def display_chat_history():
    """Display chat history"""
    st.markdown("## 💬 Chat History")
    
    if not st.session_state.chat_history:
        st.info("👋 Welcome! Ask me anything about your meetings or expenses.")
        return
    
    for i, (timestamp, user_query, assistant_response) in enumerate(st.session_state.chat_history):
        with st.container():
            # User message
            st.markdown(f"**🧑 You** _{timestamp}_")
            st.markdown(f"> {user_query}")
            
            # Assistant response
            st.markdown("**🤖 Personal Assistant**")
            st.markdown(assistant_response)
            
            st.divider()

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🤖 Personal Assistant")
    st.markdown("*Your intelligent meeting and expense management companion*")
    
    # Sidebar
    display_server_status()
    st.sidebar.divider()
    display_example_queries()
    
    # Server status warning
    if not st.session_state.server_status.get('orchestrator', False):
        st.warning("""
        ⚠️ **Orchestrator server not detected**
        
        Please ensure all three servers are running:
        ```bash
        # Terminal 1
        cd personal_assistant && uv run python servers/meeting_server.py
        
        # Terminal 2  
        cd personal_assistant && uv run python servers/expense_server.py
        
        # Terminal 3
        cd personal_assistant && uv run python servers/orchestrator_server.py
        ```
        """)
    
    # Main chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Clear input if requested
        if st.session_state.clear_input:
            st.session_state.user_input = ''
            st.session_state.clear_input = False
        
        # Handle example query selection
        if 'current_query' in st.session_state:
            st.session_state.user_input = st.session_state.current_query
            del st.session_state.current_query
        
        # Query input
        user_query = st.text_area(
            "💭 What can I help you with?",
            value=st.session_state.user_input,
            height=100,
            placeholder="Ask about meetings, expenses, or anything else...",
            key="query_input"
        )
        
        # Update session state with current input
        st.session_state.user_input = user_query
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacer
        
        send_button = st.button("🚀 Send Query", type="primary", use_container_width=True)
        
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # Process query
    if send_button and user_query.strip():
        with st.spinner("🤔 Thinking..."):
            # Send query to orchestrator
            response = asyncio.run(send_query_to_orchestrator(user_query.strip()))
            
            # Add to chat history
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.chat_history.append((timestamp, user_query.strip(), response))
            
            # Rerun to update chat display
            st.rerun()
    
    elif send_button and not user_query.strip():
        st.error("Please enter a query!")
    
    # Display chat history
    display_chat_history()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>Personal Assistant System | Powered by ACP Servers & Google Gemini</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 