# debug_research_agent.py
import os
import subprocess
import time

def start_debug_session():
    """Start ADK web with debug logging."""
    print("🔍 STARTING DEBUG SESSION")
    print("="*60)
    print("Agent has intentional bug: count_papers expects str instead of List[str]")
    print("Debug logs will show type mismatch errors")
    print("="*60)
    
    # Set debug environment
    env = os.environ.copy()
    env["ADK_LOG_LEVEL"] = "DEBUG"
    env["PYTHONUNBUFFERED"] = "1"
    
    print("Starting ADK web UI...")
    print("Open: http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    try:
        # Start with debug logging
        process = subprocess.Popen(
            ["adk", "web", "agents", "--port", "8000", "--verbose"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print output in real-time
        for line in iter(process.stdout.readline, ''):
            if "ERROR" in line or "WARNING" in line or "DEBUG" in line:
                print(f"[LOG] {line.strip()}")
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping debug session...")
        process.terminate()
    except Exception as e:
        print(f"❌ Error: {e}")

def test_agent_directly():
    """Test the agent directly to see the error."""
    print("\n🧪 DIRECT AGENT TEST")
    print("="*60)
    
    # Import the agent
    import sys
    sys.path.append("agents/research-agent")
    
    try:
        from agent import root_agent, count_papers
        
        print("Agent loaded successfully")
        print(f"Agent name: {root_agent.name}")
        print(f"Tools: {[t.__class__.__name__ for t in root_agent.tools]}")
        
        # Try to call count_papers with wrong type (simulating what agent would do)
        print("\nTesting count_papers with wrong type:")
        print("Expected: count_papers(['paper1', 'paper2']) -> 2")
        print("Actual bug: count_papers('paper1, paper2') -> ?")
        
        # This is what the bug would cause
        try:
            result = count_papers("paper1, paper2")  # Wrong: passing string instead of list
            print(f"Result with string: {result}")
            print("⚠️  Bug: Counting characters instead of list items!")
        except Exception as e:
            print(f"Error: {e}")
            
    except Exception as e:
        print(f"❌ Import/Test error: {e}")
    
    print("="*60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_agent_directly()
    else:
        start_debug_session()