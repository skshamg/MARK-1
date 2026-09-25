import threading
import winsound


class SoundFX:
    @staticmethod
    def _play_tones(tone_list):
        for freq, duration in tone_list:
            winsound.Beep(freq, duration)

    @classmethod
    def chime_wake(cls):
        """Ascending dual-tone futuristic activation chirp."""
        threading.Thread(
            target=cls._play_tones,
            args=([(880, 70), (1320, 110)],),
            daemon=True
        ).start()

    @classmethod
    def chime_vision(cls):
        """High-frequency triple-tone optical sweep cue."""
        threading.Thread(
            target=cls._play_tones,
            args=([(1200, 60), (1600, 60), (2000, 90)],),
            daemon=True
        ).start()

    @classmethod
    def chime_thinking(cls):
        """Subtle dual acknowledgment ping."""
        threading.Thread(
            target=cls._play_tones,
            args=([(950, 50), (1100, 60)],),
            daemon=True
        ).start()

    @classmethod
    def chime_abort(cls):
        """Descending disengagement tone."""
        threading.Thread(
            target=cls._play_tones,
            args=([(1400, 60), (700, 100)],),
            daemon=True
        ).start()


if __name__ == "__main__":
    print("Testing Acoustic UI...")
    SoundFX.chime_wake()