import os
import wave
import numpy as np
import sounddevice as sd
import speech_recognition as sr


class WakeWordDetector:
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.recognizer = sr.Recognizer()
        self.temp_wav = os.path.abspath("wake_buffer.wav")

        # Catches both direct names and common Indian-English phoneme captures
        self.keywords = [
            "jarvis", "javis", "jervis", "jarves", "service", 
            "charvis", "mark", "hey mark", "mark 2", "wake up"
        ]

    def poll_for_wake_phrase(self, threshold: int = 400) -> bool:
        duration = 1.4
        chunk_data = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
        )
        sd.wait()

        audio_array = chunk_data.flatten()
        rms = np.sqrt(np.mean(audio_array.astype(float) ** 2))
        if rms < threshold:
            return False

        with wave.open(self.temp_wav, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(chunk_data.tobytes())

        try:
            with sr.AudioFile(self.temp_wav) as source:
                audio = self.recognizer.record(source)

            # Prioritize Indian English acoustic profile
            text = self.recognizer.recognize_google(audio, language="en-IN").lower()

            if os.path.exists(self.temp_wav):
                os.remove(self.temp_wav)

            return any(kw in text for kw in self.keywords)
        except Exception:
            if os.path.exists(self.temp_wav):
                os.remove(self.temp_wav)
            return False