import psutil
import win32gui
import win32process

def get_foreground_app():
    """
    Returns: (app_name, pid, window_title)
    app_name = executable name (e.g., 'chrome.exe') or 'unknown'
    """
    hwnd = win32gui.GetForegroundWindow()
    if hwnd == 0:
        return ("unknown", None, "")

    window_title = win32gui.GetWindowText(hwnd)
    _, pid = win32process.GetWindowThreadProcessId(hwnd)

    app_name = "unknown"
    try:
        p = psutil.Process(pid)
        app_name = p.name()
    except Exception:
        pass

    return (app_name, pid, window_title)
