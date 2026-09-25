import time
import webbrowser
import pyautogui

# Safety fail-safe: slamming mouse to any screen corner aborts automation
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


def click_screen(x: int, y: int, clicks: int = 1, button: str = "left") -> str:
    """
    Moves the cursor to coordinate (x, y) and performs a mouse click.
    button options: 'left', 'right', 'double'
    """
    try:
        if button == "double" or clicks == 2:
            pyautogui.doubleClick(x=x, y=y)
        else:
            pyautogui.click(x=x, y=y, button=button)
        return f"Clicked at ({x}, {y}) with {button} button."
    except Exception as e:
        return f"Failed to click: {e}"


def type_keyboard(text: str, press_enter: bool = False) -> str:
    """
    Types text into whatever application window is currently focused.
    """
    try:
        pyautogui.write(text, interval=0.03)
        if press_enter:
            pyautogui.press("enter")
        return f"Typed text into active window: '{text}'."
    except Exception as e:
        return f"Failed to type: {e}"


def press_system_key(hotkey: str) -> str:
    """
    Presses a key or hotkey combination.
    Examples: 'enter', 'tab', 'esc', 'win', 'ctrl+c', 'ctrl+v', 'alt+f4'
    """
    try:
        keys = [k.strip().lower() for k in hotkey.split("+")]
        if len(keys) == 1:
            pyautogui.press(keys[0])
        else:
            pyautogui.hotkey(*keys)
        return f"Executed hotkey: '{hotkey}'."
    except Exception as e:
        return f"Failed to press key '{hotkey}': {e}"


def open_web_url(url: str) -> str:
    """
    Opens a website directly in the user's default browser (e.g. Chrome).
    """
    try:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opened {url} in browser."
    except Exception as e:
        return f"Failed to open URL: {e}"