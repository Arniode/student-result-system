"""
Data persistence layer for the application.

All student records are stored in a single JSON file inside the ``data/``
directory next to this module. The module handles all reading and writing of
records and degrades gracefully when the file is missing or corrupted.
"""

import json
import os

from student import Student

# Absolute path to the ``data`` directory. Using ``__file__`` keeps the path
# correct regardless of where the program is launched from.
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "students.json")


def ensure_data_dir():
    """Create the data directory if it does not yet exist."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except OSError as exc:
        print(f"[storage] Warning: could not create data directory: {exc}")


def load_students():
    """Load students from disk and return them as a list of Student objects.

    A missing file is treated as "no records yet" rather than an error, so the
    application can start cleanly on first run.
    """
    if not os.path.exists(DATA_FILE):
        return []

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as handle:
            raw_data = json.load(handle)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[storage] Error reading {DATA_FILE}: {exc}")
        return []

    if not isinstance(raw_data, list):
        print("[storage] Warning: data file is not a list; starting empty.")
        return []

    students = []
    for item in raw_data:
        # Skip malformed records instead of failing the entire load.
        try:
            students.append(Student.from_dict(item))
        except (TypeError, ValueError, AttributeError) as exc:
            print(f"[storage] Skipping malformed record: {exc}")
    return students


def save_students(students):
    """Persist the given list of Student objects to disk.

    Returns ``True`` on success and ``False`` on failure.
    """
    ensure_data_dir()

    try:
        data = [student.to_dict() for student in students]
    except AttributeError as exc:
        print(f"[storage] Error: expected Student objects: {exc}")
        return False

    # Write to a temporary file then atomically replace the real one so a
    # crash mid-write can never corrupt the existing data file.
    tmp_file = DATA_FILE + ".tmp"
    try:
        with open(tmp_file, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=4, ensure_ascii=False)
        os.replace(tmp_file, DATA_FILE)
        return True
    except OSError as exc:
        print(f"[storage] Error saving to {DATA_FILE}: {exc}")
        try:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
        except OSError:
            pass
        return False
