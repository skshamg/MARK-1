import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.sys_tools import get_system_telemetry, launch_application, list_files_in_directory
from tools.file_tools import write_file, read_file, append_to_file, search_files
from tools.action_tools import click_screen, type_keyboard, press_system_key, open_web_url
from tools.vision_tools import capture_screen_part
from core.memory import remember, recall, get_all_memories

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY missing from .env file!")


def build_system_prompt() -> str:
    known_memories = get_all_memories()
    return f"""
You are MARK-II (J.A.R.V.I.S.), an intelligent, sharp, and highly capable desktop system assistant.
- You have direct access to system toolkits:
  * Telemetry & Launch: get_system_telemetry, launch_application, list_files_in_directory
  * Desktop Actuation: click_screen, type_keyboard, press_system_key, open_web_url
  * File System: write_file, read_file, append_to_file, search_files
  * Memory: remember, recall
- SPATIAL VISION: You can see the user's active monitor when triggered. Analyze layouts, diagrams, and find bugs.

CRITICAL VOICE & CONVERSATIONAL RULES:
- Your response is spoken aloud via Text-to-Speech.
- NEVER read raw code blocks, long URLs, or symbols verbatim.
- Summarize errors and fixes naturally in plain English.
- Keep verbal responses concise (1 to 2 sentences).
- Autonomously actuate the desktop when requested (e.g. typing or browsing).

KNOWN MEMORIES:
{known_memories}
"""


class Mark1Brain:
    def __init__(self):
        self.client = genai.Client(api_key=api_key)
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
                click_screen,
                type_keyboard,
                press_system_key,
                open_web_url,
                remember,
                recall,
            ],
            temperature=0.3,
        )

    def _setup_chat(self):
        self.chat = self.client.chats.create(
            model=self.active_model,
            config=self._get_config()
        )

    def talk(self, user_input: str, force_vision: bool = False) -> str:
        vision_triggers = ["screen", "look", "see", "code", "window", "display", "diagram", "read this", "error"]
        needs_vision = force_vision or any(trigger in user_input.lower() for trigger in vision_triggers)

        contents = [user_input]
        if needs_vision:
            try:
                screen_part = capture_screen_part()
                contents.append(screen_part)
            except Exception as e:
                print(f"[VISION WARNING] Screen capture bypassed: {e}")

        attempts = 0
        while attempts < len(self.model_pool):
            try:
                response = self.chat.send_message(contents)
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

        return "System alert: Endpoints busy. Standing by."