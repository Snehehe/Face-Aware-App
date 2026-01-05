import time
import uuid
from datetime import datetime, timezone, timedelta

import cv2

from smartlogin.db import init_db, connect
from smartlogin.face import extract_embedding
from smartlogin.model import load_templates, identify
from smartlogin.win_apps import get_foreground_app

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def main():
    init_db()
    templates = load_templates()

    if not templates:
        print("No enrolled faces found. Run enroll.py first.")
        return

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam.")
        return

    threshold = 0.30
    required_streak = 8

    streak = 0
    active_person = None
    active_name = None
    last_score = -1

    session_id = None
    session_start = None
    log_duration = timedelta(minutes=5)
    last_app = None

    con = connect()

    print("Monitoring started. Press Q to quit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            emb, _ = extract_embedding(frame)
            label = "No face"

            if emb is not None:
                pid, name, score = identify(emb, templates, threshold)
                last_score = score

                if pid:
                    if pid == active_person:
                        streak += 1
                    else:
                        active_person = pid
                        active_name = name
                        streak = 1
                    label = f"{name} ({score:.2f}) {streak}/{required_streak}"
                else:
                    streak = max(0, streak - 1)
                    label = f"Unknown ({score:.2f})"

            cv2.putText(frame, label, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.imshow("SmartLogin", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            if session_id is None and streak >= required_streak:
                session_id = str(uuid.uuid4())
                session_start = datetime.now(timezone.utc)

                con.execute(
                    "INSERT INTO sessions(session_id, person_id, start_time, confidence) VALUES (?, ?, ?, ?)",
                    (session_id, active_person, session_start.isoformat(), float(last_score))
                )
                con.commit()

                print(f"Session started for {active_name}")

            if session_id and datetime.now(timezone.utc) - session_start <= log_duration:
                app, pid, title = get_foreground_app()
                if app != last_app:
                    con.execute(
                        "INSERT INTO app_events(session_id, event_time, app_name, pid, window_title) VALUES (?, ?, ?, ?, ?)",
                        (session_id, now_iso(), app, pid, title[:200])
                    )
                    con.commit()
                    last_app = app
                    print("App:", app)

            time.sleep(0.01)

    finally:
        cap.release()
        cv2.destroyAllWindows()
        con.close()

if __name__ == "__main__":
    main()
