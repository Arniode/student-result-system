"""
Reporting and class analysis utilities.

Provides functions to render individual report cards, sort the student list,
compute class-wide statistics and export plain-text reports.
"""

import csv
import os
from datetime import datetime

from results import SUBJECTS
from storage import DATA_DIR


class NoStudentsError(Exception):
    """Raised when an operation requires at least one student record."""


# ----------------------------------------------------------------------
# Individual report card
# ----------------------------------------------------------------------
def format_report_card(student):
    """Return a nicely formatted multi-line report card string."""
    grade = student.grade if student.grade else "N/A"

    lines = []
    border = "=" * 46
    lines.append(border)
    lines.append("               STUDENT REPORT CARD")
    lines.append(border)
    lines.append(f" Student ID    : {student.student_id}")
    lines.append(f" Full Name     : {student.full_name}")
    lines.append(f" Class/Form    : {student.class_form}")
    lines.append(f" Gender        : {student.gender}")
    lines.append(f" Date of Birth : {student.dob}")
    lines.append(f" Date Added    : {student.date_added}")
    lines.append("-" * 46)
    lines.append(" Subject           Score")
    for subject in SUBJECTS:
        score = student.scores.get(subject)
        score_text = "N/A" if score is None else f"{score}"
        lines.append(f" {subject:<16} {score_text:>6}")
    lines.append("-" * 46)
    lines.append(f" Total          : {student.total}")
    lines.append(f" Average        : {student.average}")
    lines.append(f" Grade          : {grade}")
    lines.append(border)
    return "\n".join(lines)


def generate_report_card(student):
    """Convenience wrapper returning a student's report card string."""
    return format_report_card(student)


# ----------------------------------------------------------------------
# Sorting
# ----------------------------------------------------------------------
def sort_students(students, key="average"):
    """Return a sorted copy of the student list.

    Args:
        students: list of Student instances.
        key:      one of "average" (highest first), "name" or "id" (A-Z).

    Raises:
        ValueError: if ``key`` is not supported.
    """
    if key in ("average", "score"):
        return sorted(students, key=lambda s: (s.average or 0), reverse=True)
    if key == "name":
        return sorted(students, key=lambda s: s.full_name.lower())
    if key == "id":
        return sorted(students, key=lambda s: s.student_id)
    raise ValueError(f"Unsupported sort key: {key}")


# ----------------------------------------------------------------------
# Class statistics
# ----------------------------------------------------------------------
def class_statistics(students):
    """Compute highest, lowest and average performance for the class.

    Returns a dictionary with the following keys:
        ``highest``, ``lowest`` (Student instances),
        ``class_average`` (float) and ``count`` (int).

    Raises:
        NoStudentsError: if no records are available.
    """
    if not students:
        raise NoStudentsError("No student records available for analysis.")

    # Use only students that have grades, falling back to all students if none
    # have any scores recorded yet.
    graded = [s for s in students if s.average is not None]
    pool = graded or students

    highest = max(pool, key=lambda s: s.average or 0)
    lowest = min(pool, key=lambda s: s.average or 0)
    class_average = round(sum(s.average or 0 for s in pool) / len(pool), 2)

    return {
        "highest": highest,
        "lowest": lowest,
        "class_average": class_average,
        "count": len(students),
    }


def format_class_statistics(stats):
    """Return a human-readable text summary of class statistics."""
    highest = stats["highest"]
    lowest = stats["lowest"]
    lines = [
        "  ---- CLASS STATISTICS ----",
        f"  Number of students : {stats['count']}",
        f"  Highest average    : {highest.average}  ({highest.full_name})",
        f"  Lowest average     : {lowest.average}  ({lowest.full_name})",
        f"  Class average      : {stats['class_average']}",
    ]
    return "\n".join(lines)


# ----------------------------------------------------------------------
# Report export
# ----------------------------------------------------------------------
def export_report(students, filename="class_report.txt"):
    """Export a full ranked class report to a plain-text file.

    The file is written into the ``data`` directory. The absolute path of the
    created file is returned.

    Raises:
        NoStudentsError: if there are no records to export.
    """
    if not students:
        raise NoStudentsError("No student records to export.")

    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)

    stats = class_statistics(students)
    ranked = sort_students(students, key="average")

    lines = [
        "=" * 62,
        "   STUDENT RESULT MANAGEMENT SYSTEM - CLASS REPORT",
        "=" * 62,
        f" Generated      : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f" Total students : {stats['count']}",
        f" Class average  : {stats['class_average']}",
        f" Highest        : {stats['highest'].full_name} "
        f"({stats['highest'].average})",
        f" Lowest         : {stats['lowest'].full_name} "
        f"({stats['lowest'].average})",
        "-" * 62,
        f" {'Rank':<5}{'ID':<10}{'Name':<24}{'Avg':>8}{'Grade':>8}",
        "-" * 62,
    ]
    for rank, student in enumerate(ranked, start=1):
        grade = student.grade if student.grade else "N/A"
        lines.append(
            f" {rank:<5}{student.student_id:<10}{student.full_name:<24}"
            f"{student.average:>8}{grade:>8}"
        )
    lines.append("=" * 62)

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

    return path


def export_csv(students, filename="class_report.csv"):
    """Export all student records to a CSV file.

    The file is written into the ``data`` directory so it can be opened in a
    spreadsheet application (Excel, Google Sheets, etc.). The absolute path of
    the created file is returned.

    Raises:
        NoStudentsError: if there are no records to export.
    """
    if not students:
        raise NoStudentsError("No student records to export.")

    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)

    header = [
        "Student ID", "Full Name", "Class/Form", "Gender", "DOB",
        *SUBJECTS, "Total", "Average", "Grade", "Date Added",
    ]

    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        for student in students:
            row = [
                student.student_id,
                student.full_name,
                student.class_form,
                student.gender,
                student.dob,
                *[student.scores.get(subject, "") for subject in SUBJECTS],
                student.total,
                student.average,
                student.grade if student.grade else "",
                student.date_added,
            ]
            writer.writerow(row)

    return path
