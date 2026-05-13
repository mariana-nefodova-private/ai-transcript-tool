import json
import os
import uuid
from datetime import datetime

LIBRARY_FILE = os.path.join(os.path.dirname(__file__), "library.json")


def _load() -> dict:
    if not os.path.exists(LIBRARY_FILE):
        return {"projects": {}, "transcripts": {}}
    with open(LIBRARY_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict) -> None:
    with open(LIBRARY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_all() -> dict:
    return _load()


def create_project(name: str) -> dict:
    data = _load()
    pid = str(uuid.uuid4())
    data["projects"][pid] = {
        "id": pid,
        "name": name,
        "created_at": datetime.now().isoformat(),
    }
    _save(data)
    return data["projects"][pid]


def rename_project(pid: str, name: str) -> dict | None:
    data = _load()
    if pid not in data["projects"]:
        return None
    data["projects"][pid]["name"] = name
    _save(data)
    return data["projects"][pid]


def delete_project(pid: str) -> bool:
    data = _load()
    if pid not in data["projects"]:
        return False
    del data["projects"][pid]
    to_delete = [tid for tid, t in data["transcripts"].items() if t.get("project_id") == pid]
    for tid in to_delete:
        del data["transcripts"][tid]
    _save(data)
    return True


def save_transcript(filename: str, transcript: str, project_id: str | None = None) -> dict:
    data = _load()
    tid = str(uuid.uuid4())
    data["transcripts"][tid] = {
        "id": tid,
        "project_id": project_id,
        "filename": filename,
        "transcript": transcript,
        "created_at": datetime.now().isoformat(),
    }
    _save(data)
    return data["transcripts"][tid]


def delete_transcript(tid: str) -> bool:
    data = _load()
    if tid not in data["transcripts"]:
        return False
    del data["transcripts"][tid]
    _save(data)
    return True
