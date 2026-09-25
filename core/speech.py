import asyncio
import ctypes
import os
import edge_tts


class SpeechEngine:
    def __init__(self, voice: str = "en-GB-RyanNeural"):
        """
        voice options:
        - 'en-GB-RyanNeural' (Crisp, sophisticated British JARVIS)
        - 'en-US-ChristopherNeural' (Deep American conversational)
        """
        self.voice = voice
        self.temp_file = os.path.abspath("mark1_voice.mp3")
        self.winmm = ctypes.windll.winmm

    def speak(self, text: str):
        clean_text = text.strip()
        if not clean_text:
            return

        # Strip markdown syntax so it doesn't speak asterisks or hashes
        clean_text = (
            clean_text.replace("*", "")
            .replace("#", "")
            .replace("`", "")
            .replace(">", "")
            .replace("- ", "")
        )

        try:
            # 1. Synthesize neural audio file
            asyncio.run(self._generate_speech(clean_text))

            # 2. Play directly using Windows Multimedia API
            self._play_native()
        except Exception as e:
            # Fallback to local SAPI if network drops
            self._fallback_sapi(clean_text)

    async def _generate_speech(self, text: str):
        communicator = edge_tts.Communicate(text, self.voice)
        await communicator.save(self.temp_file)

    def _play_native(self):
        """Uses Windows native winmm.dll to play the audio buffer cleanly."""
        # Convert path to 8.3 short path format to handle paths with spaces
        short_buf = ctypes.create_unicode_buffer(260)
        ctypes.windll.kernel32.GetShortPathNameW(self.temp_file, short_buf, 260)
        short_path = short_buf.value or self.temp_file

        # Windows MCI audio pipeline
        self.winmm.mciSendStringW("close mark1_audio", None, 0, None)
        self.winmm.mciSendStringW(f'open "{short_path}" type mpegvideo alias mark1_audio', None, 0, None)
        self.winmm.mciSendStringW("play mark1_audio wait", None, 0, None)
        self.winmm.mciSendStringW("close mark1_audio", None, 0, None)

        # Cleanup temporary audio file
        if os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except Exception:
                pass

    def _fallback_sapi(self, text: str):
        sanitized = text.replace("'", "").replace('"', "")
        ps_cmd = (
            f"Add-Type -AssemblyName System.Speech; "
            f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$synth.Rate = 1; "
            f"$synth.Speak('{sanitized}')"
        )
        os.system(f'powershell -NoProfile -Command "{ps_cmd}"')


# --- Direct Audio Test ---
if __name__ == "__main__":
    print("Testing Mark-1 Neural Voice Engine...")
    speaker = SpeechEngine()
    speaker.speak("Good day, sir. Mark One neural audio is fully operational and awaiting your command.")
    print("Audio check completed.")