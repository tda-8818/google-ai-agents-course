# run_test.py - FIXED
import os
import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner

load_dotenv()

from agent import root_agent

async def main():
    print("🚀 Testing Home Automation Agent")
    print("="*50)
    
    # FIX: Pass the agent to InMemoryRunner
    runner = InMemoryRunner(agent=root_agent)  # ← ADD agent parameter
    
    # Simple test
    query = "Turn on the living room lights"
    print(f"User: {query}")
    
    try:
        events = await runner.run_debug(query)
        
        # Print agent responses
        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(f"Agent: {part.text}")
                        
                    # Check for tool calls
                    if part.function_call:
                        print(f"🛠️  Tool called: {part.function_call.name}")
                        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())