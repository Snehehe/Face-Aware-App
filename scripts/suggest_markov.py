import json
import os
import subprocess
from smartlogin.db import connect

MODEL_PATH = "data/markov_model.json"
AUTO_OPEN = False

APP_LAUNCH_MAP = {
    "chrome.exe": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    # "Code.exe": r"C:\Users\snehs\AppData\Local\Programs\Microsoft VS Code\Code.exe",
}

IGNORE = {"python.exe", "WindowsTerminal.exe", "explorer.exe"}

def get_latest_person_and_last_app():
    con = connect()
    row = con.execute("""
      SELECT s.person_id,
             (SELECT ae.app_name FROM app_events ae
              WHERE ae.session_id = s.session_id
              ORDER BY ae.event_time DESC
              LIMIT 1) AS last_app
      FROM sessions s
      ORDER BY s.start_time DESC
      LIMIT 1
    """).fetchone()
    con.close()
    return row

def main():
    if not os.path.exists(MODEL_PATH):
        print("No Markov model yet. Run: python -m scripts.train_markov")
        return

    pid, last_app = get_latest_person_and_last_app()
    if not pid or not last_app or last_app in IGNORE:
        print("Not enough real app history yet (need last_app).")
        return

    with open(MODEL_PATH, "r", encoding="utf-8") as f:
        model = json.load(f)

    key = f"{pid}|{last_app}"
    top = model.get(key, [])
    if not top:
        print(f"No learned transition from {last_app} yet.")
        return

    print(f"Based on last app = {last_app}, next suggestions:")
    for app, cnt in top[:3]:
        print(f"  - {app} (seen {cnt}x)")

    best_app = top[0][0]
    exe = APP_LAUNCH_MAP.get(best_app)

    if AUTO_OPEN and exe:
        print(f"Auto-opening: {best_app}")
        subprocess.Popen(exe, shell=True)
    else:
        print(f"Top pick: {best_app}")
        if not exe:
            print("No launch path configured yet for this app.")

if __name__ == "__main__":
    main()
