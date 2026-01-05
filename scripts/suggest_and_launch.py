import json
import os
import subprocess
from datetime import datetime
from smartlogin.db import connect

MODEL_PATH = "data/app_model.json"

# Safer default: suggest only
AUTO_OPEN = False

# Map exe name -> full path (add the apps you care about)
APP_LAUNCH_MAP = {
    "chrome.exe": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    # "Code.exe": r"C:\Users\snehs\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    # "slack.exe": r"C:\Users\snehs\AppData\Local\slack\slack.exe",
}

def get_latest_session():
    con = connect()
    row = con.execute("""
      SELECT s.person_id, p.display_name, s.start_time
      FROM sessions s
      JOIN people p ON p.person_id = s.person_id
      ORDER BY s.start_time DESC
      LIMIT 1
    """).fetchone()
    con.close()
    return row

def parse_dt(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))

def main():
    if not os.path.exists(MODEL_PATH):
        print("No model yet. Run: python -m scripts.train_model")
        return

    sess = get_latest_session()
    if not sess:
        print("No sessions in DB yet.")
        return

    person_id, name, start_time = sess
    dt = parse_dt(start_time)
    key = f"{person_id}|{dt.weekday()}|{dt.hour}"

    with open(MODEL_PATH, "r", encoding="utf-8") as f:
        model = json.load(f)

    top = model.get(key, [])
    if not top:
        print(f"No learned suggestion yet for {name} at weekday={dt.weekday()} hour={dt.hour}.")
        return

    print(f"Suggestions for {name} (weekday={dt.weekday()}, hour={dt.hour}):")
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
            print("No launch path configured for this app yet in APP_LAUNCH_MAP.")

if __name__ == "__main__":
    main()
