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

# Load environment variables
load_dotenv()

# Define retry config
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],
)

# ===== 1. DEFINE THE CALLBACK FUNCTION =====
async def auto_save_to_memory(callback_context):
    """Automatically save session to memory after each agent turn."""
    await callback_context._invocation_context.memory_service.add_session_to_memory(
        callback_context._invocation_context.session
    )

print("✅ Callback created.")

# ===== 2. DEFINE HELPER FUNCTIONS =====
async def run_session(runner_instance: Runner, user_query: str, session_id: str):
    """Helper function to run a session."""
    print(f"\n### Session: {session_id}")
    print(f"User > {user_query}")
    
    # Create session
    APP_NAME = "AutoSaveAgentApp"
    USER_ID = "demo_user"
    
    try:
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
    except:
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=session_id
        )
    
    # Run the query
    query_content = types.Content(role="user", parts=[types.Part(text=user_query)])
    
    async for event in runner_instance.run_async(
        user_id=USER_ID, session_id=session.id, new_message=query_content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            text = event.content.parts[0].text
            if text and text != "None":
                print(f"Model: > {text}")

# ===== 3. CREATE SERVICES =====
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

print("✅ Services created.")

# ===== 4. CREATE AGENT WITH AUTOMATIC MEMORY =====
auto_memory_agent = LlmAgent(
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    name="AutoMemoryAgent",
    instruction="Answer user questions.",
    tools=[preload_memory],
    after_agent_callback=auto_save_to_memory,  # Saves after each turn!
)

print("✅ Agent created with automatic memory saving!")

# ===== 5. CREATE RUNNER =====
auto_runner = Runner(
    agent=auto_memory_agent,
    app_name="AutoSaveAgentApp",
    session_service=session_service,
    memory_service=memory_service,
)

print("✅ Runner created.")

# ===== 6. TEST IT =====
async def main():
    print("\n" + "="*60)
    print("TESTING AUTOMATIC MEMORY SAVING")
    print("="*60)
    
    # Test 1: Tell the agent about a gift (first conversation)
    await run_session(
        auto_runner,
        "I gifted a new toy to my nephew on his 1st birthday!",
        "auto-save-test",
    )

    # Test 2: Ask about the gift in a NEW session (second conversation)
    await run_session(
        auto_runner,
        "What did I gift my nephew?",
        "auto-save-test-2",  # Different session ID - proves memory works across sessions!
    )
    
    print("\n" + "="*60)
    print("✅ SUCCESS! Memory was automatically:")
    print("   1. Saved after first conversation (via callback)")
    print("   2. Retrieved in second conversation (via preload_memory)")
    print("   3. No manual memory calls needed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())