import numpy as np
from smartlogin.db import connect
from smartlogin.face import cosine_sim

def load_templates():
    con = connect()
    rows = con.execute("""
        SELECT p.person_id, p.display_name, t.embedding
        FROM face_templates t
        JOIN people p ON p.person_id = t.person_id
    """).fetchall()
    con.close()

    templates = []
    for person_id, name, emb_blob in rows:
        emb = np.frombuffer(emb_blob, dtype=np.float32)
        emb = emb / (np.linalg.norm(emb) + 1e-12)
        templates.append((person_id, name, emb))
    return templates

def identify(embedding, templates, threshold=0.30):
    best = (None, None, -1.0)
    for pid, name, emb in templates:
        s = cosine_sim(embedding, emb)
        if s > best[2]:
            best = (pid, name, s)

    if best[2] >= threshold:
        return best
    return (None, None, best[2])
