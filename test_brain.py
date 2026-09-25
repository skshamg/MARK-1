import os
import time
from dotenv import load_dotenv
from google import genai

# 1. Load your secret API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("[ERROR] GEMINI_API_KEY not found in .env file!")
    exit()

print("[1/3] API Key loaded successfully.")
print("[2/3] Asking Google servers for active models on your account...")

client = genai.Client(api_key=api_key)

# 2. Discover every model your key is allowed to use
valid_models = []
try:
    for m in client.models.list():
        # Only keep models that can chat / generate text
        actions = getattr(m, 'supported_actions', [])
        if "generateContent" in actions:
            # Clean up the name (remove 'models/' prefix if present)
            name = m.name.replace("models/", "")
            valid_models.append(name)
            
    print(f"--> Found {len(valid_models)} usable models.")
except Exception as e:
    print(f"[NOTE] Could not fetch model list: {e}")
    # Default backup list
    valid_models = ["gemini-3.8-flash", "gemini-flash-latest", "gemini-2.0-flash"]

# 3. Connect to the first model that responds
print("[3/3] Initiating handshake with Mark-1 core...")

connected = False
for model_name in valid_models:
    # Prioritize flash models for speed
    if "flash" not in model_name and len(valid_models) > 3:
        continue

    print(f"--> Testing link with: {model_name}...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents="Confirm online status in exactly 8 words as JARVIS."
        )
        print("\n" + "=" * 50)
        print(f"RESPONSE FROM MARK-1 CORE ({model_name}):")
        print(response.text.strip())
        print("=" * 50)
        print("\n>> Handshake successful. Mark-1 brain is online.")
        connected = True
        break
    except Exception as e:
        # Print the real error so we know what happened
        print(f"    [FAILED] {model_name} error: {e}")
        time.sleep(1)

if not connected:
    print("\n[ERROR] All models failed. Check the error lines above.")