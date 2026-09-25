import os
import subprocess
import psutil


def get_system_telemetry() -> str:
    """
    Retrieves current real-time telemetry from the laptop:
    CPU usage, RAM consumption, and battery status.
    """
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    battery = psutil.sensors_battery()

    battery_info = "Desktop / No battery detected"
    if battery:
        plugged_status = "Plugged In" if battery.power_plugged else "On Battery"
        battery_info = f"{battery.percent}% ({plugged_status})"

    report = (
        f"Telemetry Report:\n"
        f"- CPU Usage: {cpu_usage}%\n"
        f"- RAM Usage: {memory.percent}% (Used {round(memory.used / (1024**3), 2)} GB of {round(memory.total / (1024**3), 2)} GB)\n"
        f"- Battery: {battery_info}"
    )
    return report


def launch_application(app_name: str) -> str:
    """
    Launches desktop applications by common name or system alias.
    """
    # Map common English names to their actual Windows commands
    app_map = {
        # Core System Tools
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "task manager": "taskmgr.exe",
        "taskmgr": "taskmgr.exe",
        "file explorer": "explorer.exe",
        "explorer": "explorer.exe",
        "terminal": "wt.exe",  # Windows Terminal
        "cmd": "cmd.exe",

        # Microsoft Office Suite
        "word": "winword",
        "ms word": "winword",
        "microsoft word": "winword",
        "excel": "excel",
        "ms excel": "excel",
        "powerpoint": "powerpnt",
        "ppt": "powerpnt",

        # Browsers & Media
        "chrome": "chrome",
        "google chrome": "chrome",
        "edge": "msedge",
        "brave": "brave",
        "spotify": "spotify",
        "vlc": "vlc",

        # Development
        "vs code": "code",
        "vscode": "code",
        "code": "code"
    }

    clean_name = app_name.strip().lower()
    command = app_map.get(clean_name)

    if not command:
        return f"Mark-1 protocol: '{app_name}' is not in the recognized app registry."

    try:
        # 'start' tells Windows to find and launch the app from anywhere on the PC
        subprocess.Popen(f"start {command}", shell=True)
        return f"Confirmed: Launched {clean_name}."
    except Exception as e:
        return f"Unable to launch {clean_name}: {str(e)}"


def list_files_in_directory(path: str = ".") -> str:
    """
    Lists files and directories at the given path. Defaults to current directory.
    """
    try:
        target_path = os.path.abspath(path)
        items = os.listdir(target_path)
        if not items:
            return f"Directory '{target_path}' is empty."
        
        file_list = "\n".join([f"- {item}" for item in items[:25]])
        return f"Files in {target_path}:\n{file_list}"
    except Exception as e:
        return f"Error reading path: {str(e)}"