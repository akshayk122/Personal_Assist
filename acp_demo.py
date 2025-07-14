from collections.abc import AsyncGenerator
from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Server,RunYield,RunYieldResume
import os


from crewai import Agent, Task, Crew,LLM
from crewai_tools import RagTool

import nest_asyncio
nest_asyncio.apply()

os.environ["GOOGLE_API_KEY"]="API_KEY"

server = Server()
llm=LLM(model="gemini/gemini-2.0-flash",max_tokens=1000)

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

rag_tool = RagTool(config=config,chunk_size=1000,chunk_overlap=100)

rag_tool.add("/Users/AKSHAY/Documents/Dummy_Projects/ACP/resume.json",data_type="json")

@server.agent(name="web_agent")
async def agent(input:list[Message])->AsyncGenerator[RunYield,RunYieldResume]:
    "This agent is used to answer questions about the json file"
    web_agent = Agent(
        role="Resume QA Agent",
        goal="Answer questions from a resume.json file",
        backstory="You are an expert at analyzing and extracting data from resumes in JSON format.",
        llm=llm,
        tools=[rag_tool],
        allow_delegation=True,
        verbose=True
    )

    task1 = Task(
        description="Answer the user's question about the resume content.",
        expected_output="Detailed but concise answer from the JSON resume.",
        agent=web_agent,
        verbose=True
    )
    crew=Crew(agents=[web_agent],tasks=[task1],verbose=True)
    task1_result=await crew.kickoff_async()

    yield Message(parts=[MessagePart(content=str(task1_result))])

if __name__ == "__main__":
    server.run(port=8000)



