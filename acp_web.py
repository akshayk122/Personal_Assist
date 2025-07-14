from collections.abc import AsyncGenerator
from acp_sdk.models import Message,MessagePart
from acp_sdk.server import Server,Context,RunYield,RunYieldResume
from smolagents import CodeAgent,DuckDuckGoSearchTool,LiteLLMModel,VisitWebpageTool
import logging
from dotenv import load_dotenv

load_dotenv()

server=Server()

model=LiteLLMModel(model_id="gemini-2.0-flash",max_tokens=1000)

@server.agent(name="website_agent")
async def agent(input:list[Message],context:Context)->AsyncGenerator[RunYield,RunYieldResume]:
    "This agent is used to answer questions about the website"
    agent=CodeAgent(tools=[DuckDuckGoSearchTool(),VisitWebpageTool()],model=model,verbose=True)
    prompt=input[0].parts[0].content
    response=agent.run(prompt)
    yield Message(parts=[MessagePart(content=str(response))])

if __name__ == "__main__":
    server.run(port=8001)

