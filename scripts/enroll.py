import uuid
import time
from datetime import datetime, timezone

import cv2

from smartlogin.db import init_db, connect
from smartlogin.face import extract_embedding

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def main():
    init_db()

    name = input("Enter your name (e.g. Sneh): ").strip()
    if not name:
        print("Name required.")
        return

    person_id = str(uuid.uuid4())

    con = connect()
    con.execute(
        "INSERT INTO people(person_id, display_name) VALUES (?, ?)",
        (person_id, name)
    )
    con.commit()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam.")
        return

    print("\nENROLLMENT MODE")
    print("Press SPACE to capture a face")
    print("Press Q to finish\n")

    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.putText(
            frame,
            f"{name} | Captured: {count}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow("Enroll", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        if key == 32:  # SPACE
            emb, quality = extract_embedding(frame)
            if emb is None:
                print("No face detected. Try again.")
                continue

            con.execute(
                "INSERT INTO face_templates(person_id, embedding, created_at) VALUES (?, ?, ?)",
                (person_id, emb.tobytes(), now_iso())
            )
            con.commit()
            count += 1
            print(f"Captured #{count}")
            time.sleep(0.3)

    cap.release()
    cv2.destroyAllWindows()
    con.close()

    print(f"\nEnrollment complete. {count} samples saved.")
    print(f"Person ID: {person_id}")

if __name__ == "__main__":
    main()
