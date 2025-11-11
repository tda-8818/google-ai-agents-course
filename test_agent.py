# test_agent.py - For running and testing your agent
import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
import asyncio

load_dotenv()

async def main():
    # Define agent
    root_agent = Agent(
        name="helpful_assistant",
        model=Gemini(model="gemini-2.5-flash-lite"),
        description="A simple agent that can answer general questions.",
        instruction="You are a helpful assistant. Use Google Search for current info or if unsure.",
        tools=[google_search],
    )
    
    # Create runner and test
    runner = InMemoryRunner(agent=root_agent)
    
    response = await runner.run_debug(
        "What is Agent Development Kit from Google? What languages is the SDK available in?"
    )
    
    print("Response:", response.final_output)

if __name__ == "__main__":
    asyncio.run(main())