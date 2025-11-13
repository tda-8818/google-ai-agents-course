# agents/session-state-agent/agent.py
import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5, exp_base=7, initial_delay=1, http_status_codes=[429, 500, 503, 504]
)

# Tool to save user info to session state
def save_userinfo(tool_context: ToolContext, user_name: str, country: str) -> dict:
    """Tool to record and save user name and country in session state."""
    tool_context.state["user:name"] = user_name
    tool_context.state["user:country"] = country
    return {"status": "success", "message": f"Saved {user_name} from {country}"}

# Tool to retrieve user info from session state  
def retrieve_userinfo(tool_context: ToolContext) -> dict:
    """Tool to retrieve user name and country from session state."""
    user_name = tool_context.state.get("user:name", "Not provided yet")
    country = tool_context.state.get("user:country", "Not provided yet")
    return {"status": "success", "user_name": user_name, "country": country}

# Create agent with session state tools
root_agent = Agent(
    name="session_state_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    description="A chatbot that remembers user information across conversations",
    instruction="""You are a helpful assistant that can remember user information.

    When users tell you their name and country, use save_userinfo to store it.
    When users ask about their information, use retrieve_userinfo to recall it.
    
    Important: The ADK web UI automatically maintains session state, so you can remember information within the same conversation!
    """,
    tools=[
        FunctionTool(func=save_userinfo),
        FunctionTool(func=retrieve_userinfo)
    ],
)

print("✅ Session state agent ready for ADK Web UI!")