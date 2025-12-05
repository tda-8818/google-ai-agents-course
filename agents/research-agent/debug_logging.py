import logging
import os

print("🔧 SETTING UP DEBUGGING ENVIRONMENT")
print("="*60)

# Clean up old logs
log_files = ["logger.log", "web.log", "adk_debug.log"]
for log_file in log_files:
    if os.path.exists(log_file):
        os.remove(log_file)
        print(f"🧹 Cleaned up {log_file}")

# Configure logging with DEBUG level
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("adk_debug.log"),
        logging.StreamHandler()  # Also print to console
    ]
)

# Create a custom logger for ADK
adk_logger = logging.getLogger("google.adk")
adk_logger.setLevel(logging.DEBUG)

print("✅ Logging configured:")
print("   - Debug logs: adk_debug.log")
print("   - Console output: ON")
print("   - Log level: DEBUG")
print("="*60)