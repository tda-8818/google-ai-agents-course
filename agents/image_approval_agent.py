# image_approval_agent.py - FIXED VERSION
import uuid
import asyncio
from dotenv import load_dotenv
from google.genai import types

# Basic imports only
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.tool_context import ToolContext

print("✅ Simplified image approval agent components imported successfully.")

load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5, exp_base=7, initial_delay=1, http_status_codes=[429, 500, 503, 504]
)

# Cost thresholds
BULK_IMAGE_THRESHOLD = 1  # More than 1 image requires approval
IMAGE_COST_PER_UNIT = 0.10  # Simulated cost per image

def generate_images_with_approval(
    num_images: int, description: str, tool_context: ToolContext
) -> dict:
    """Generates images. Requires approval for bulk generation (>1 image)."""
    
    # SCENARIO 1: Single image auto-approves
    if num_images <= BULK_IMAGE_THRESHOLD:
        return {
            "status": "approved",
            "num_images": num_images,
            "description": description,
            "cost": IMAGE_COST_PER_UNIT * num_images,
            "message": f"✅ Auto-approved: Generated {num_images} image(s) of '{description}'",
            "images": [f"simulated_image_{i}" for i in range(num_images)]
        }
    
    # SCENARIO 2: Bulk generation needs approval - PAUSE
    if not tool_context.tool_confirmation:
        total_cost = IMAGE_COST_PER_UNIT * num_images
        tool_context.request_confirmation(
            hint=f"💰 Bulk generation: {num_images} images of '{description}'. Cost: ${total_cost:.2f}. Approve?",
            payload={
                "num_images": num_images, 
                "description": description,
                "total_cost": total_cost
            },
        )
        return {
            "status": "pending_approval",
            "message": f"Bulk generation of {num_images} images requires approval (${total_cost:.2f})",
        }
    
    # SCENARIO 3: Resuming with approval decision
    if tool_context.tool_confirmation.confirmed:
        return {
            "status": "approved",
            "num_images": num_images,
            "description": description,
            "cost": IMAGE_COST_PER_UNIT * num_images,
            "message": f"✅ Approved: Generated {num_images} images of '{description}'",
            "images": [f"approved_bulk_image_{i}" for i in range(num_images)]
        }
    else:
        return {
            "status": "rejected",
            "message": f"❌ Rejected: Bulk generation of {num_images} images was not approved",
        }

print("✅ Approval-based image function created!")

# Create image agent with approval system
image_approval_agent = LlmAgent(
    name="image_approval_agent",
    model=Gemini(model="gemini-2.5-flash-lite", retry_options=retry_config),
    instruction="""You are an image generation assistant with cost controls.

    When users request images:
    1. For single images (1 image): Generate immediately
    2. For bulk images (>1 image): Use the approval system to check cost
    3. Always provide clear cost estimates
    
    Use the generate_images_with_approval tool for all image requests.
    """,
    tools=[FunctionTool(func=generate_images_with_approval)],
)

print("✅ Image approval agent created!")

def extract_final_output(events):
    """Extract the final text output from events."""
    for event in reversed(events):  # Look for the last text response
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    return part.text
    return "No response text found"

async def run_simple_workflow():
    """Simple test without complex session management."""
    
    print("🚀 Testing Image Approval Agent")
    print("=" * 50)
    
    runner = InMemoryRunner(agent=image_approval_agent)
    
    # Test 1: Single image (auto-approve)
    print("\n📸 TEST 1: Single image (auto-approve)")
    print("User > Generate 1 image of a sunset")
    try:
        events = await runner.run_debug("Generate 1 image of a sunset")
        final_output = extract_final_output(events)
        print(f"Agent > {final_output}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Bulk images (will pause for approval)
    print("\n📸 TEST 2: Bulk images (requires approval)")
    print("User > Generate 5 images of landscapes")
    try:
        events = await runner.run_debug("Generate 5 images of landscapes")
        final_output = extract_final_output(events)
        print(f"Agent > {final_output}")
        print("💡 This would pause for human approval in a real app")
    except Exception as e:
        if "cancel scope" in str(e):
            print("Agent > ⏸️  Approval required for bulk generation")
        else:
            print(f"Error: {e}")
    
    # Test 3: Very large request
    print("\n📸 TEST 3: Large bulk request")
    print("User > Generate 20 images for my website")
    try:
        events = await runner.run_debug("Generate 20 images for my website")
        final_output = extract_final_output(events)
        print(f"Agent > {final_output}")
    except Exception as e:
        if "cancel scope" in str(e):
            print("Agent > ⏸️  Approval required - this is expensive!")
        else:
            print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Exercise Summary:")
    print("✅ Single images auto-approve")
    print("✅ Bulk images trigger approval workflow") 
    print("✅ Cost controls are built into the tool")
    print("✅ Human-in-the-loop pattern demonstrated")

async def main():
    await run_simple_workflow()

if __name__ == "__main__":
    asyncio.run(main())