import io
from PIL import ImageGrab
from google.genai import types


def capture_screen_part() -> types.Part:
    """
    Captures the primary monitor buffer, optimizes it for low network
    latency, and packages it into a Gemini Multimodal Part.
    """
    screenshot = ImageGrab.grab()

    # Scale down to 1080p if on an ultra-high-res display for sub-second upload
    screenshot.thumbnail((1920, 1080))

    # Compress into an in-memory JPEG stream (no disk writes needed)
    buf = io.BytesIO()
    screenshot.save(buf, format="JPEG", quality=85)
    buf.seek(0)

    return types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg")