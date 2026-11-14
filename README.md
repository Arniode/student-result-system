# Student Result Management System

A production-ready, modular command-line application written in Python for
recording students, storing their subject scores, computing results and
generating reports.

## Features

- **Object-oriented data model** (`Student` class) with biographical details,
  five subject scores and derived results (total, average, grade).
- **Automatic grading**:
  | Grade | Average score |
  |-------|---------------|
  | A     | 70 - 100      |
  | B     | 60 - 69       |
  | C     | 50 - 59       |
  | D     | 45 - 49       |
  | F     | 0 - 44        |
- **Persistent storage** in a JSON file (`data/students.json`) using safe,
  atomic writes.
- **Reporting & analysis** including individual report cards, sorting by
  average/name/ID, class statistics and export to plain-text or CSV.
- **Interactive menu** with robust input validation and error handling.
- **Student ID validation** using a regular expression (1-5 letters followed
  by 1-6 digits, e.g. `S001`, `STU12345`).
- **Exception handling** demonstrating `try` / `except` / `else` / `finally`
  when reading and writing the data file.

## Project Structure

```
student_result_system/
├── main.py       # Interactive CLI menu and application entry point
├── student.py    # Student class (data model)
├── results.py    # Scoring & grading utilities
├── storage.py    # JSON persistence (load/save)
├── reports.py    # Report cards, sorting, statistics & export
├── data/
│   └── students.json   # Persistent record storage
└── README.md
```

## Requirements

- Python 3.7+ (no third-party packages required).

## Getting Started

Run the application from the project directory:

```bash
cd student_result_system
python main.py
```

> The program can also be launched with `python student_result_system/main.py`
> from the parent folder — the data file location is resolved relative to the
> module, not the current working directory.

## Web Interface (optional)

The project also ships a Flask web UI (`app.py` + `templates/`) that reuses the
same `student.py`, `results.py`, `storage.py` and `reports.py` modules so the
system can be hosted as a live website.

Run it locally:

```bash
pip install -r requirements.txt
python app.py
```

Then open <http://127.0.0.1:5000>.

### Deploying to Render (free)

1. Push this repository to GitHub.
2. Go to <https://render.com> and sign in with GitHub (no card required).
3. Click **New** → **Blueprint**, select the repository, and confirm.
   Render reads `render.yaml` and creates a free web service automatically.
4. After a few minutes you will get a live URL like
   `https://student-result-system.onrender.com` — use this as your
   hosting/live-project link.

> Note: the free tier puts the service to sleep after ~15 minutes of
> inactivity, so the first visit may take ~30–50 seconds to wake up. Also, the
> JSON data file is stored on the instance's ephemeral disk, so data resets on
> redeploy — the CLI version keeps permanent local storage.

## Menu Reference

| Option | Description                                       |
|--------|---------------------------------------------------|
| 1      | Add a new student & record 5 subject scores        |
| 2      | View all registered students                       |
| 3      | Search student by ID or name                       |
| 4      | Update student info or scores                       |
| 5      | Delete a student record                             |
| 6      | Display an individual report card                   |
| 7      | Sort students & view class statistics (and export) |
| 8      | Save and exit                                        |

All data is saved automatically after every change and once more when the
program exits, so records are never lost unexpectedly.

## Data Format

Records are stored as a JSON array. Example entry:

```json
{
    "student_id": "S001",
    "full_name": "Jane Doe",
    "class_form": "Form 3A",
    "gender": "Female",
    "dob": "2009-04-12",
    "scores": {
        "Mathematics": 78,
        "English": 82,
        "Physics": 65,
        "Chemistry": 71,
        "Biology": 69
    },
    "total": 365,
    "average": 73.0,
    "grade": "A",
    "date_added": "2026-11-09T10:30:00"
}
```
