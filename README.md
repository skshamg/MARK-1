# PROJECT JARVIS // Autonomous Desktop AI Agent

A modular, multimodal desktop assistant built in Python and powered by Google Gemini Flash models. Designed with an autonomous tool-calling pipeline, localized persistent memory, spatial vision, and a glassmorphic PyQt6 desktop HUD.

---

## Evolution: Mark-1 vs. Mark-2

| Capability | Mark-1 (`main.py`) | Mark-2 (`mark2_app.py`) |
| :--- | :--- | :--- |
| **Interface** | Terminal CLI prompt | Frameless PyQt6 Glassmorphism HUD |
| **Visual Telemetry** | Plain text printouts | Live Arc Reactor animation + CPU/RAM/BAT dials |
| **Input System** | Keyboard typing | Hands-free wake word (`Jarvis`) & Push-to-Talk |
| **Language Support** | Standard English | Indian-English (`en-IN`) acoustic phonetic tuning |
| **Sensory Cortex** | Auditory synthesis only | Multimodal Spatial Vision (Screen analysis) |
| **OS Actuation** | File I/O & App launch | Mouse clicking, keyboard simulation, web navigation |
| **Audio Controls** | Blocking speech playback | Non-blocking speech with instant `Esc` interrupt |

---

## Features

- **Spatial Vision:** Takes instant monitor captures to debug code, analyze schematics, or summarize open browser tabs via Gemini 3.5 Flash.
- **Persistent Neural State:** Built-in SQLite memory engine (`mark1_memory.db`) retaining preferences and user facts across sessions.
- **Acoustic & Subtitle UI:** Frequency-modulated system chimes paired with live transcriptions directly inside the HUD.
- **Fail-Safe Core:** Multi-model pool rotation (`gemini-3.5-flash-lite`, `gemini-3.8-flash`, `gemini-3.5-flash`) handling rate limits and network latency seamlessly.

---

## Controls & Shortcuts (Mark-2)

- **Wake Word:** Say `"Jarvis"` or `"Mark"` to activate hands-free listening.
- **Push-to-Talk:** Press `Ctrl + Shift + Space` (or click the Arc Reactor) to give a vocal command.
- **Optical Sweep (Vision):** Press `Ctrl + Shift + V` to capture your active screen and speak your query.
- **Emergency Silence:** Press `Esc` at any time to instantly cut off speech and return to standby.

---

## Project Structure

```text
MARK-1/
├── core/
│   ├── audio_fx.py      # Native zero-dependency UI chimes
│   ├── brain.py         # Gemini multimodal brain & tool execution
│   ├── ears.py          # Adaptive en-IN speech recognition
│   ├── memory.py        # SQLite persistent memory engine
│   ├── speech.py        # Non-blocking neural TTS & audio sanitizer
│   └── wake_word.py     # Background voice activity detector
├── hud/
│   ├── hud_window.py    # PyQt6 glassmorphism overlay & Arc Reactor
│   └── style.css        # QSS sci-fi styling sheet
├── tools/
│   ├── action_tools.py  # Mouse & keyboard OS actuation
│   ├── file_tools.py    # Autonomous file manipulation
│   ├── sys_tools.py     # Hardware telemetry & app launcher
│   └── vision_tools.py  # Display buffer capture pipeline
├── main.py              # Mark-1 terminal entry point
├── mark2_app.py         # Mark-2 master GUI entry point
├── requirements.txt     # Python environment dependencies
└── .gitignore           # Ignores .env and SQLite binaries


Install dependencies:
pip install -r requirements.txt

Configure API Key:
Create a .env file in the root directory:
Code snippet
GEMINI_API_KEY=your_gemini_api_key_here

Launch:
For Mark-2 (Full HUD Experience):
python mark2_app.py

For Mark-1 (Lightweight Terminal Mode):
python main.py
