import json
import os
from collections import defaultdict, Counter
from datetime import datetime
from smartlogin.db import connect

OUT_PATH = "data/app_model.json"

# Apps to ignore in learning
IGNORE = {"python.exe", "WindowsTerminal.exe", "explorer.exe"}

def parse_dt(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))

def bucket(dt):
    return (dt.weekday(), dt.hour)

def main():
    con = connect()

    # Pull session + all app events
    rows = con.execute("""
      SELECT s.person_id, s.start_time, ae.event_time, ae.app_name
      FROM sessions s
      JOIN app_events ae ON ae.session_id = s.session_id
      ORDER BY s.start_time DESC, ae.event_time ASC
    """).fetchall()

    con.close()

    # For each session, find the first "real" app event
    first_real = {}  # (person_id, weekday, hour) -> Counter(app)
    counts = defaultdict(Counter)

    # Group events by (person_id, start_time)
    current_key = None
    current_events = []

    for person_id, start_time, event_time, app in rows:
        key = (person_id, start_time)
        if current_key is None:
            current_key = key

        if key != current_key:
            # process previous session
            pid, st = current_key
            dt = parse_dt(st)
            b = bucket(dt)
            for a in current_events:
                if a not in IGNORE:
                    counts[(pid, b)].update([a])
                    break
            current_key = key
            current_events = []

        current_events.append(app)

    # process last group
    if current_key is not None:
        pid, st = current_key
        dt = parse_dt(st)
        b = bucket(dt)
        for a in current_events:
            if a not in IGNORE:
                counts[(pid, b)].update([a])
                break

    model = {}
    for (person_id, b), counter in counts.items():
        model[f"{person_id}|{b[0]}|{b[1]}"] = counter.most_common(5)

    os.makedirs("data", exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)

    print(f"Wrote {OUT_PATH} with {len(model)} time-buckets.")

if __name__ == "__main__":
    main()
