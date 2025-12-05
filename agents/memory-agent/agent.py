from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory, preload_memory
from google.genai import types
from dotenv import load_dotenv
load_dotenv()
import asyncio


print("✅ ADK components imported successfully.")

async def run_session(
    runner_instance: Runner, user_queries: list[str] | str, session_id: str = "default"
):
    """Helper function to run queries in a session and display responses."""
    print(f"\n### Session: {session_id}")

    # Create or retrieve session
    try:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
    except:
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )

    # Convert single query to list
    if isinstance(user_queries, str):
        user_queries = [user_queries]

    # Process each query
    for query in user_queries:
        print(f"\nUser > {query}")
        query_content = types.Content(role="user", parts=[types.Part(text=query)])

        # Stream agent response
        async for event in runner_instance.run_async(
            user_id=USER_ID, session_id=session.id, new_message=query_content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text
                if text and text != "None":
                    print(f"Model: > {text}")


print("✅ Helper functions defined.")

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

memory_service = (
    InMemoryMemoryService()
)  # ADK's built-in Memory Service for development and testing

# Define constants used throughout the notebook
APP_NAME = "MemoryDemoApp"
USER_ID = "demo_user"

# Create agent
user_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="MemoryDemoAgent",
    instruction="Answer user questions in simple words. Use load_memory tool if you need to recall past conversations.",
    tools=[
        preload_memory
    ],  # Agent now has access to Memory and can search it whenever it decides to!
)

print("✅ Agent with load_memory tool created.")

  # Create Session Service
session_service = InMemorySessionService()  # Handles conversations

# Create runner with BOTH services
# Create a new runner with the updated agent
runner = Runner(
    agent=user_agent,
    app_name=APP_NAME,
    session_service=session_service,
    memory_service=memory_service,
)

print("✅ Agent and Runner created with memory support!")

async def main():
  

    await run_session(runner, "What is my favorite color?", "color-test")
    await run_session(runner, "My birthday is on March 15th.", "birthday-session-01")

    # Manually save the session to memory
    birthday_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id="birthday-session-01"
    )

    await memory_service.add_session_to_memory(birthday_session)

    print("✅ Birthday session saved to memory!")

    # Test retrieval in a NEW session
    await run_session(
        runner, "When is my birthday?", "birthday-session-02"  # Different session ID
    )
    
    # ===== ADD THIS SEARCH SECTION =====
    print("\n" + "="*60)
    print("SECTION 5.5: MANUAL MEMORY SEARCH")
    print("="*60)
    
    # Test different search queries like the example
    test_queries = [
        "What is the user's favorite color?",
        "what color does the user like",
        "haiku", 
        "age",
        "preferred hue",
        "birthday",
        "March"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Searching for: '{query}'")
        
        search_response = await memory_service.search_memory(
            app_name=APP_NAME, 
            user_id=USER_ID, 
            query=query
        )
        
        print(f"  Found {len(search_response.memories)} relevant memories")
        
        # Show first few results
        for i, memory in enumerate(search_response.memories[:3], 1):  # Limit to 3
            if memory.content and memory.content.parts:
                text = memory.content.parts[0].text[:80]
                print(f"  {i}. [{memory.author}]: {text}...")
    
    print("\n" + "="*60)
    print("OBSERVATIONS:")
    print("• 'What is the user's favorite color?' finds color memories")
    print("• 'haiku' finds the haiku response") 
    print("• 'age' finds nothing (not mentioned)")
    print("• 'preferred hue' might find color memories")
    print("• 'birthday' finds birthday memories")
    print("• Memory search is keyword-based!")
    print("="*60)

asyncio.run(main())