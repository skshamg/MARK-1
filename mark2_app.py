import sys
import time
import keyboard
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal

from hud.hud_window import JarvisHUD
from core.brain import Mark1Brain
from core.speech import SpeechEngine
from core.ears import EarEngine


class AutonomousCoreWorker(QThread):
    update_hud = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.running = True
        self.brain = None
        self.speaker = None
        self.ears = None
        self.trigger_mode = None
        self.abort_requested = False

    def trigger_voice(self):
        if not self.trigger_mode:
            self.trigger_mode = "VOICE"

    def trigger_vision(self):
        if not self.trigger_mode:
            self.trigger_mode = "VISION"

    def interrupt(self):
        """Immediately halts active speech, thinking, or listening."""
        self.abort_requested = True
        self.trigger_mode = None
        if self.speaker:
            self.speaker.stop()
        self.update_hud.emit("ONLINE", "Action aborted. Ready.")

    def run(self):
        self.update_hud.emit("INITIALIZING", "Loading Mark-II systems...")

        self.brain = Mark1Brain()
        self.speaker = SpeechEngine()
        self.ears = EarEngine()

        time.sleep(0.5)
        self.update_hud.emit("ONLINE", "Ctrl+Shift+Space: Talk | Esc: Mute")
        self.speaker.speak("Mark Two systems armed. Press Escape at any time to silence me.")

        while self.running:
            if not self.trigger_mode:
                time.sleep(0.05)
                continue

            self.abort_requested = False
            current_mode = self.trigger_mode
            self.trigger_mode = None

            # 1. Listening State (with smart pause detection)
            if current_mode == "VISION":
                self.update_hud.emit("VISION ACTIVE", "Capturing screen... Speak now.")
            else:
                self.update_hud.emit("LISTENING", "Listening (take your time)...")

            spoken_text = self.ears.listen_smart(max_duration=15, silence_tolerance=1.8)

            if self.abort_requested:
                continue

            if not spoken_text:
                self.update_hud.emit("ONLINE", "No voice captured. Standing by.")
                continue

            # 2. Thinking State
            self.update_hud.emit("THINKING", f'"{spoken_text}"')

            if spoken_text.lower() in ["exit", "quit", "shutdown", "abort"]:
                self.update_hud.emit("STANDBY", "Deactivating...")
                self.speaker.speak("Shutting down. Goodbye, sir.")
                self.running = False
                break

            force_vision = (current_mode == "VISION")
            reply = self.brain.talk(spoken_text, force_vision=force_vision)

            if self.abort_requested:
                continue

            # 3. Speaking State (Interruptible)
            self.update_hud.emit("SPEAKING", f'"{spoken_text}"')
            self.speaker.speak(reply)

            if not self.abort_requested:
                self.update_hud.emit("ONLINE", "Ctrl+Shift+Space: Talk | Esc: Mute")
            time.sleep(0.2)


def main():
    app = QApplication(sys.argv)

    hud = JarvisHUD()
    hud.show()

    worker = AutonomousCoreWorker()
    worker.update_hud.connect(hud.set_agent_state)

    # Click Arc Reactor to talk or interrupt
    hud.reactor_triggered.connect(worker.trigger_voice)

    # Clean, Conflict-Free Global Hotkeys
    try:
        keyboard.add_hotkey("ctrl+shift+space", worker.trigger_voice)
        keyboard.add_hotkey("ctrl+shift+v", worker.trigger_vision)
        keyboard.add_hotkey("esc", worker.interrupt)
    except Exception as e:
        print(f"[HOTKEY ALERT] Failed to hook shortcuts: {e}")

    worker.start()

    exit_code = app.exec()
    worker.running = False
    keyboard.unhook_all()
    worker.wait(2000)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()