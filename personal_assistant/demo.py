#!/usr/bin/env python3
"""
Demo script for Personal Assistant System
Tests the orchestrator and shows example interactions
"""

import asyncio
import sys
import os
from acp_sdk.client import Client
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

async def test_server_connection(url: str, agent_name: str, server_name: str) -> bool:
    """Test if a server is running and responsive"""
    try:
        async with Client(base_url=url) as client:
            response = await client.run_sync(
                agent=agent_name,
                input="Hello, are you working?"
            )
            print(f"{Fore.GREEN}✅ {server_name} is running")
            return True
    except Exception as e:
        print(f"{Fore.RED}❌ {server_name} not available: {str(e)}")
        return False

async def run_demo_queries():
    """Run a series of demo queries"""
    
    print(f"{Fore.CYAN}{Style.BRIGHT}🤖 Personal Assistant Demo")
    print("=" * 50)
    
    # Test server connections
    print(f"\n{Fore.YELLOW}Checking server status...")
    
    servers = [
        ("http://localhost:8100", "meeting_manager", "Meeting Manager"),
        ("http://localhost:8200", "expense_tracker", "Expense Tracker"),
        ("http://localhost:8300", "personal_assistant", "Orchestrator")
    ]
    
    all_running = True
    for url, agent, name in servers:
        if not await test_server_connection(url, agent, name):
            all_running = False
    
    if not all_running:
        print(f"\n{Fore.RED}❌ Some servers are not running!")
        print(f"{Fore.YELLOW}Please start all servers first:")
        print("  Terminal 1: make meeting")
        print("  Terminal 2: make expense")
        print("  Terminal 3: make orchestrator")
        return
    
    print(f"\n{Fore.GREEN}✅ All servers are running!")
    
    # Demo queries
    demo_queries = [
        "What can you help me with?",
        "Schedule a team standup tomorrow at 9 AM in Conference Room A",
        "I spent $15.99 on coffee this morning",
        "Show me my upcoming meetings",
        "What did I spend on food yesterday?",
        "Do I have any meetings this week and what's my total spending?"
    ]
    
    print(f"\n{Fore.CYAN}{Style.BRIGHT}Running Demo Queries...")
    print("=" * 50)
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{Fore.BLUE}{Style.BRIGHT}Query {i}: {query}")
        print("-" * 60)
        
        try:
            async with Client(base_url="http://localhost:8300") as client:
                response = await client.run_sync(
                    agent="personal_assistant",
                    input=query
                )
                print(f"{Fore.WHITE}{response.output[0].parts[0].content}")
                
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}")
        
        # Small delay between queries
        await asyncio.sleep(1)
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}✅ Demo completed!")
    print(f"\n{Fore.CYAN}💡 Try the Streamlit UI for a better experience:")
    print(f"   {Fore.WHITE}make streamlit")
    print(f"   {Fore.WHITE}Then open: http://localhost:8501")

async def main():
    """Main demo function"""
    try:
        await run_demo_queries()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Demo interrupted by user")
    except Exception as e:
        print(f"\n{Fore.RED}Demo failed: {str(e)}")

if __name__ == "__main__":
    print(f"{Fore.MAGENTA}Starting Personal Assistant Demo...")
    asyncio.run(main()) 