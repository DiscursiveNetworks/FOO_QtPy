import json
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Path to your JSON config file
config_path = "WA25/config_Guevara_NIH.json"

# Step 1: Load the config file
try:
    with open(config_path, "r") as f:
        config = json.load(f)
    print("✅ Config file loaded successfully.")
except Exception as e:
    print("❌ Error loading config file:", e)
    exit(1)

# Step 2: Check a few key fields
print("\n📂 CONFIG SUMMARY:")
print(f"Project name: {config['CONFIG'].get('project_name', 'N/A')}")
print(f"Author: {config['CONFIG'].get('author', 'N/A')}")
print(f"CWD: {config['CONFIG'].get('CWD', 'N/A')}")

# Step 3: Check if API keys are set in environment
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

if anthropic_key:
    print("\n🔑 Anthropic API key found.")
else:
    print("\n⚠️ Anthropic API key not found. Check your .env file or environment variables.")

if openai_key:
    print("🔑 OpenAI API key found.")
else:
    print("⚠️ OpenAI API key not found. Check your .env file or environment variables.")
