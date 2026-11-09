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
  average/name/ID, class statistics and plain-text report export.
- **Interactive menu** with robust input validation and error handling.

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
