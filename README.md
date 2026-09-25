# MARK-1 // Autonomous Desktop System Agent

Mark-1 is a modular, system-level autonomous AI agent built in Python and powered by Google Gemini with dynamic tool execution.

## Core Capabilities
- **Neural Core**: Multi-model automatic failover using Gemini Flash models via the official Google GenAI SDK.
- **Hardware Telemetry**: Real-time CPU, RAM, and battery monitoring via `psutil`.
- **System Automation**: Whitelisted execution of Windows desktop utilities and applications.
- **File System Engine**: Autonomous creation, reading, and directory scanning for local scripts and notes.
- **Neural Voice**: Crisp, studio-grade speech output running on Microsoft neural voices.
- **Persistent State**: Embedded SQLite memory engine for fact retention across sessions.

## Project Structure
```text
MARK-1/
├── core/
│   ├── brain.py        # Gemini client, tool calling, and failover
│   ├── memory.py       # SQLite persistent memory engine
│   └── speech.py       # Neural text-to-speech engine
├── tools/
│   ├── file_tools.py   # Autonomous file manipulation
│   └── sys_tools.py    # Hardware telemetry and app launching
├── main.py             # Interactive console loop
├── requirements.txt    # Python dependencies
└── .gitignore          # Environment & binary exclusion rules
