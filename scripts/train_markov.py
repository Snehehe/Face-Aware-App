import json
import os
from collections import defaultdict, Counter
from smartlogin.db import connect

OUT_PATH = "data/markov_model.json"
IGNORE = {"python.exe", "WindowsTerminal.exe", "explorer.exe"}

def main():
    con = connect()
    rows = con.execute("""
      SELECT s.person_id, ae.event_time, ae.app_name
      FROM sessions s
      JOIN app_events ae ON ae.session_id = s.session_id
      ORDER BY s.start_time DESC, ae.event_time ASC
    """).fetchall()
    con.close()

    # transitions[(person_id, prev_app)] -> Counter(next_app)
    transitions = defaultdict(Counter)

    prev = None
    prev_pid = None

    for pid, _, app in rows:
        if app in IGNORE:
            continue

        if prev is not None and pid == prev_pid:
            transitions[(pid, prev)].update([app])

        prev = app
        prev_pid = pid

    model = {f"{pid}|{prev_app}": counter.most_common(5)
             for (pid, prev_app), counter in transitions.items()}

    os.makedirs("data", exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)

    print(f"Wrote {OUT_PATH} with {len(model)} states.")

if __name__ == "__main__":
    main()
