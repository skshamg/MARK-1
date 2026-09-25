import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Add root folder to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.sys_tools import get_system_telemetry, launch_application, list_files_in_directory
from tools.file_tools import write_file, read_file, append_to_file, search_files
from core.memory import remember, recall, get_all_memories

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY missing from .env file!")


def build_system_prompt() -> str:
    known_memories = get_all_memories()
    return f"""
You are MARK-1 (J.A.R.V.I.S.), an intelligent, sharp, and highly capable desktop system assistant.
- You have direct access to your local system toolkits:
  * Telemetry & Apps: get_system_telemetry, launch_application, list_files_in_directory
  * File System: write_file, read_file, append_to_file, search_files
  * Memory Engine: remember (store key/value), recall (retrieve memories)
- When the user tells you to remember something, or asks what you remember about them or a project, call the memory tools autonomously.
- Be concise, direct, professional, and slightly witty.
- Never output raw JSON. Address the user with calm confidence.

KNOWN LONG-TERM MEMORIES:
{known_memories}
"""


class Mark1Brain:
    def __init__(self):
        self.client = genai.Client(api_key=api_key)
        # 3.5 Flash-Lite provides sub-second responses without server bottlenecks
        self.model_pool = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-3.5-flash"]
        self.current_model_idx = 0
        self.active_model = self.model_pool[self.current_model_idx]
        self._setup_chat()

    def _get_config(self):
        return types.GenerateContentConfig(
            system_instruction=build_system_prompt(),
            tools=[
                get_system_telemetry,
                launch_application,
                list_files_in_directory,
                write_file,
                read_file,
                append_to_file,
                search_files,
                remember,
                recall,
            ],
            temperature=0.6,
        )

    def _setup_chat(self):
        self.chat = self.client.chats.create(
            model=self.active_model,
            config=self._get_config()
        )

    def talk(self, user_input: str) -> str:
        attempts = 0
        while attempts < len(self.model_pool):
            try:
                response = self.chat.send_message(user_input)
                return response.text.strip()
            except Exception as e:
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str or "429" in err_str:
                    attempts += 1
                    self.current_model_idx = (self.current_model_idx + 1) % len(self.model_pool)
                    self.active_model = self.model_pool[self.current_model_idx]
                    print(f"\n[SYSTEM ALERT: Switching core to {self.active_model}...]")
                    self._setup_chat()
                    time.sleep(1)
                else:
                    return f"System alert: Communication pipeline encountered an error: {e}"

        return "System alert: All Gemini neural endpoints are experiencing high demand."