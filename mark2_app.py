import sys
import time
import keyboard
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal

from hud.hud_window import JarvisHUD
from core.brain import Mark1Brain
from core.speech import SpeechEngine
from core.ears import EarEngine
from core.wake_word import WakeWordDetector
from core.audio_fx import SoundFX


class AutonomousCoreWorker(QThread):
    update_hud = pyqtSignal(str, str)
    update_subs = pyqtSignal(str, str)  # (Speaker, Text)

    def __init__(self):
        super().__init__()
        self.running = True
        self.brain = None
        self.speaker = None
        self.ears = None
        self.wake_detector = None
        self.trigger_mode = None
        self.abort_requested = False

    def trigger_voice(self):
        if not self.trigger_mode:
            SoundFX.chime_wake()
            self.trigger_mode = "VOICE"

    def trigger_vision(self):
        if not self.trigger_mode:
            SoundFX.chime_vision()
            self.trigger_mode = "VISION"

    def interrupt(self):
        self.abort_requested = True
        self.trigger_mode = None
        SoundFX.chime_abort()
        if self.speaker:
            self.speaker.stop()
        self.update_hud.emit("ONLINE", "Action aborted.")
        self.update_subs.emit("SYSTEM", "Emergency stop triggered. Standing by.")

    def run(self):
        self.update_hud.emit("INITIALIZING", "Loading Mark-II neural systems...")
        self.update_subs.emit("SYSTEM", "Calibrating en-IN acoustic receptors...")

        self.brain = Mark1Brain()
        self.speaker = SpeechEngine()
        self.ears = EarEngine()
        self.wake_detector = WakeWordDetector()

        time.sleep(0.5)
        self.update_hud.emit("ONLINE", "Ready")
        self.update_subs.emit("MARK-II", "All systems nominal, sir. Vocal wake word active.")
        SoundFX.chime_wake()
        self.speaker.speak("Mark Two online. Systems nominal, sir.")

        while self.running:
            if not self.trigger_mode:
                if self.wake_detector.poll_for_wake_phrase():
                    self.trigger_voice()
                else:
                    time.sleep(0.05)
                    continue

            self.abort_requested = False
            current_mode = self.trigger_mode
            self.trigger_mode = None

            # 1. Listening State
            if current_mode == "VISION":
                self.update_hud.emit("VISION ACTIVE", "Capturing screen...")
                self.update_subs.emit("SYSTEM", "Optical sweep active. Speak command...")
            else:
                self.update_hud.emit("LISTENING", "Listening...")
                self.update_subs.emit("SYSTEM", "Listening to your voice...")

            spoken_text = self.ears.listen_smart(max_duration=15, silence_tolerance=1.8)

            if self.abort_requested:
                continue

            if not spoken_text:
                self.update_hud.emit("ONLINE", "No voice captured.")
                self.update_subs.emit("SYSTEM", "No voice detected. Standing by.")
                continue

            # Subtitle what the user just said
            self.update_subs.emit("YOU", spoken_text)

            # 2. Thinking State
            SoundFX.chime_thinking()
            self.update_hud.emit("THINKING", f'"{spoken_text}"')

            if spoken_text.lower() in ["exit", "quit", "shutdown", "abort"]:
                SoundFX.chime_abort()
                self.update_hud.emit("STANDBY", "Deactivating...")
                self.update_subs.emit("MARK-II", "Shutting down. Goodbye, sir.")
                self.speaker.speak("Shutting down. Goodbye, sir.")
                self.running = False
                break

            force_vision = (current_mode == "VISION")
            reply = self.brain.talk(spoken_text, force_vision=force_vision)

            if self.abort_requested:
                continue

            # 3. Speaking State + Subtitles
            self.update_hud.emit("SPEAKING", f'"{spoken_text}"')
            self.update_subs.emit("MARK-II", reply)
            self.speaker.speak(reply)

            if not self.abort_requested:
                self.update_hud.emit("ONLINE", "Ready")
            time.sleep(0.2)


def main():
    app = QApplication(sys.argv)

    hud = JarvisHUD()
    hud.show()

    worker = AutonomousCoreWorker()
    worker.update_hud.connect(hud.set_agent_state)
    worker.update_subs.connect(hud.set_subtitles)

    hud.reactor_triggered.connect(worker.trigger_voice)

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