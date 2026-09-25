import asyncio
import ctypes
import os
import re
import time
import edge_tts


class SpeechEngine:
    def __init__(self, voice: str = "en-GB-RyanNeural"):
        self.voice = voice
        self.temp_file = os.path.abspath("mark1_voice.mp3")
        self.winmm = ctypes.windll.winmm
        self.is_speaking = False
        self._abort = False

    def sanitize_for_speech(self, text: str) -> str:
        """Strips raw code blocks, markdown junk, and translates snake_case."""
        # 1. Remove markdown code blocks completely
        cleaned = re.sub(r"```[\s\S]*?```", " [code snippet omitted] ", text)

        # 2. Remove inline backticks
        cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)

        # 3. Replace snake_case underscores with spaces (e.g., sys_tools -> sys tools)
        cleaned = cleaned.replace("_", " ")

        # 4. Remove formatting symbols
        cleaned = re.sub(r"[*#>`~|/\\{}]", " ", cleaned)

        # 5. Clean up multiple spaces
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def stop(self):
        """Immediately interrupts and terminates active speech playback."""
        self._abort = True
        try:
            self.winmm.mciSendStringW("stop mark1_audio", None, 0, None)
            self.winmm.mciSendStringW("close mark1_audio", None, 0, None)
        except Exception:
            pass
        self.is_speaking = False

    def speak(self, text: str):
        clean_text = self.sanitize_for_speech(text)
        if not clean_text:
            return

        self.stop()  # Stop any prior speech before beginning
        self._abort = False
        self.is_speaking = True

        try:
            # Generate neural audio buffer
            asyncio.run(self._generate_speech(clean_text))

            if self._abort:
                return

            self._play_non_blocking()
        except Exception:
            self.is_speaking = False

    async def _generate_speech(self, text: str):
        communicator = edge_tts.Communicate(text, self.voice)
        await communicator.save(self.temp_file)

    def _play_non_blocking(self):
        """Plays audio asynchronously so it can be interrupted at any millisecond."""
        short_buf = ctypes.create_unicode_buffer(260)
        ctypes.windll.kernel32.GetShortPathNameW(self.temp_file, short_buf, 260)
        short_path = short_buf.value or self.temp_file

        self.winmm.mciSendStringW("close mark1_audio", None, 0, None)
        self.winmm.mciSendStringW(f'open "{short_path}" type mpegvideo alias mark1_audio', None, 0, None)
        self.winmm.mciSendStringW("play mark1_audio", None, 0, None)  # No "wait" keyword

        # Poll playback status every 50ms to allow instant cancellation
        status_buf = ctypes.create_unicode_buffer(128)
        while not self._abort:
            self.winmm.mciSendStringW("status mark1_audio mode", status_buf, 128, None)
            if status_buf.value != "playing":
                break
            time.sleep(0.05)

        self.winmm.mciSendStringW("stop mark1_audio", None, 0, None)
        self.winmm.mciSendStringW("close mark1_audio", None, 0, None)
        self.is_speaking = False

        if os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except Exception:
                pass