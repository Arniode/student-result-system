"""
Command-line interface for the Student Result Management System.

Run with:  python main.py
"""

from datetime import datetime

from student import Student
from results import SUBJECTS, MIN_SCORE, MAX_SCORE
from storage import load_students, save_students
from reports import (
    format_report_card,
    sort_students,
    class_statistics,
    format_class_statistics,
    export_report,
    NoStudentsError,
)


# ----------------------------------------------------------------------
# Input helpers
# ----------------------------------------------------------------------
def prompt_non_empty(label):
    """Prompt until the user provides a non-empty string."""
    while True:
        value = input(label).strip()
        if value:
            return value
        print("Value cannot be empty. Please try again.")


def prompt_int(label):
    """Prompt until the user provides a valid whole number."""
    while True:
        raw = input(label).strip()
        try:
            return int(raw)
        except ValueError:
            print("Invalid number. Please enter a whole number.")


def prompt_float(label, lo=MIN_SCORE, hi=MAX_SCORE):
    """Prompt until the user provides a number within ``lo`` and ``hi``."""
    while True:
        raw = input(label).strip()
        try:
            value = float(raw)
        except ValueError:
            print("Invalid score. Please enter a number.")
            continue
        if value < lo or value > hi:
            print(f"Score must be between {lo} and {hi}.")
            continue
        return value


def prompt_gender():
    """Prompt for a gender, returning a normalised label."""
    while True:
        value = input("Gender (M/F/O): ").strip().upper()
        if value == "M":
            return "Male"
        if value == "F":
            return "Female"
        if value == "O":
            return "Other"
        print("Please enter M, F or O.")


def prompt_dob():
    """Prompt for a date of birth in YYYY-MM-DD format."""
    while True:
        raw = input("Date of birth (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("Invalid date. Please use the YYYY-MM-DD format.")


def prompt_scores():
    """Prompt for and return the five subject scores as a dictionary."""
    print("\nEnter scores for the five subjects "
          f"(each between {MIN_SCORE} and {MAX_SCORE}):")
    scores = {}
    for subject in SUBJECTS:
        scores[subject] = prompt_float(f"  {subject:<12}: ")
    return scores


# ----------------------------------------------------------------------
# Lookup helpers
# ----------------------------------------------------------------------
def find_by_id(students, student_id):
    """Return the first student matching the given ID (case-insensitive)."""
    student_id = student_id.lower()
    for student in students:
        if student.student_id.lower() == student_id:
            return student
    return None


def find_by_name(students, name):
    """Return all students whose full name contains the given text."""
    name = name.lower()
    return [s for s in students if name in s.full_name.lower()]


def select_student(students):
    """Prompt the user to pick a single student, or return None."""
    if not students:
        print("No students registered yet.")
        return None

    query = prompt_non_empty("Enter student ID or full name: ")

    exact = find_by_id(students, query)
    if exact:
        return exact

    matches = find_by_name(students, query)
    if not matches:
        print(f"No matching student found for '{query}'.")
        return None
    if len(matches) == 1:
        return matches[0]

    print("Multiple matches found:")
    for i, student in enumerate(matches, start=1):
        print(f"  {i}. {student}")
    choice = prompt_int("Select a number (0 to cancel): ")
    if 0 < choice <= len(matches):
        return matches[choice - 1]
    print("Selection cancelled.")
    return None


# ----------------------------------------------------------------------
# Display helpers
# ----------------------------------------------------------------------
def print_student_table(students, title):
    """Print a column-aligned table of students."""
    if not students:
        print("No students to display.")
        return
    header = (f"{'ID':<10}{'Name':<24}{'Class':<14}{'Avg':>8}{'Grade':>8}")
    print(title)
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    for student in students:
        grade = student.grade if student.grade else "N/A"
        print(
            f"{student.student_id:<10}{student.full_name:<24}"
            f"{student.class_form:<14}{student.average:>8}{grade:>8}"
        )
    print("-" * len(header))


# ----------------------------------------------------------------------
# Menu actions
# ----------------------------------------------------------------------
def add_student(students):
    """Add a new student and record the five subject scores."""
    print("=" * 48)
    print("                  ADD NEW STUDENT")
    print("=" * 48)

    student_id = prompt_non_empty("Student ID: ")
    if find_by_id(students, student_id):
        print(f"A student with ID '{student_id}' already exists.")
        return

    full_name = prompt_non_empty("Full name: ")
    class_form = prompt_non_empty("Class/Form: ")
    gender = prompt_gender()
    dob = prompt_dob()
    scores = prompt_scores()

    student = Student(student_id, full_name, class_form, gender, dob,
                      scores=scores)
    students.append(student)

    if save_students(students):
        print(f"\nStudent '{full_name}' added successfully "
              f"(Avg: {student.average}, Grade: {student.grade}).")
    else:
        print("\nStudent added to memory but could not be saved to disk.")


def view_students(students):
    """List all registered students."""
    print("=" * 48)
    print("              REGISTERED STUDENTS")
    print("=" * 48)
    if not students:
        print("No students registered yet.")
        return
    print_student_table(students, f"Total: {len(students)} student(s)")
    print()


def search_student(students):
    """Search for students by ID or name and show their report cards."""
    print("=" * 48)
    print("                 SEARCH STUDENT")
    print("=" * 48)
    query = prompt_non_empty("Enter student ID or name to search: ")

    results = []
    exact = find_by_id(students, query)
    if exact:
        results.append(exact)
    results.extend(find_by_name(students, query))

    # De-duplicate while preserving order.
    seen = set()
    unique = []
    for student in results:
        if student.student_id not in seen:
            seen.add(student.student_id)
            unique.append(student)

    if not unique:
        print(f"No matching student found for '{query}'.")
        return

    for student in unique:
        print()
        print(format_report_card(student))


def _update_details(student):
    """Update a student's biographical details."""
    print("\n(Leave a field blank to keep its current value.)")
    full_name = input(f"Full name [{student.full_name}]: ").strip()
    class_form = input(f"Class/Form [{student.class_form}]: ").strip()
    gender = input(f"Gender [{student.gender}]: ").strip()

    dob = input(f"DOB [{student.dob}]: ").strip()
    if dob:
        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format; keeping previous DOB.")
            dob = ""

    if full_name or class_form or gender or dob:
        student.update_details(
            full_name=(full_name or None),
            class_form=(class_form or None),
            gender=(gender or None),
            dob=(dob or None),
        )
        print("Details updated successfully.")
    else:
        print("No changes made.")


def _update_scores(student):
    """Update one or all of a student's subject scores."""
    subject_list = list(SUBJECTS)
    print("\nChoose a subject to update:")
    for i, subject in enumerate(subject_list, start=1):
        current = student.scores.get(subject, "N/A")
        print(f"  {i}. {subject:<12} (current: {current})")
    print("  0. Update all subjects")

    choice = prompt_int("Choice: ")

    if choice == 0:
        student.update_scores(prompt_scores())
        print("All subject scores updated.")
    elif 1 <= choice <= len(subject_list):
        subject = subject_list[choice - 1]
        score = prompt_float(f"New score for {subject}: ")
        student.update_single_score(subject, score)
        print(f"{subject} updated to {score}.")
    else:
        print("Invalid choice.")
        return

    print(f"New results -> Average: {student.average}, Grade: {student.grade}")


def update_student(students):
    """Update a student's details or scores."""
    print("=" * 48)
    print("                 UPDATE STUDENT")
    print("=" * 48)
    student = select_student(students)
    if student is None:
        return

    print(f"Updating record for: {student.full_name}")
    while True:
        print("\nWhat would you like to update?")
        print("  1. Personal details")
        print("  2. Subject scores")
        print("  0. Back")
        choice = prompt_int("Choice: ")

        if choice == 0:
            return
        if choice == 1:
            _update_details(student)
            break
        if choice == 2:
            _update_scores(student)
            break
        print("Invalid choice.")

    if not save_students(students):
        print("Warning: changes applied in memory but could not be saved.")


def delete_student(students):
    """Delete a student record after confirmation."""
    print("=" * 48)
    print("                 DELETE STUDENT")
    print("=" * 48)
    student = select_student(students)
    if student is None:
        return

    print()
    print(format_report_card(student))
    confirm = input(
        f"\nDelete '{student.full_name}'? This cannot be undone (y/N): "
    ).strip().lower()

    if confirm != "y":
        print("Deletion cancelled.")
        return

    students.remove(student)
    if save_students(students):
        print(f"Student '{student.full_name}' deleted successfully.")
    else:
        print("Student removed from memory but could not be saved to disk.")


def show_report_card(students):
    """Display the report card for a selected student."""
    print("=" * 48)
    print("              INDIVIDUAL REPORT CARD")
    print("=" * 48)
    student = select_student(students)
    if student is None:
        return
    print()
    print(format_report_card(student))


def export_report_menu(students):
    """Prompt for a filename and export the class report."""
    filename = input("Report filename [class_report.txt]: ").strip()
    filename = filename or "class_report.txt"
    try:
        path = export_report(students, filename)
        print(f"Report exported to:\n  {path}")
    except NoStudentsError:
        print("No student records to export.")
    except OSError as exc:
        print(f"Could not write report: {exc}")


def sort_and_statistics(students):
    """Sort students and display class statistics."""
    if not students:
        print("No students registered yet.")
        return

    while True:
        print("=" * 48)
        print("        SORT STUDENTS & CLASS STATISTICS")
        print("=" * 48)
        print("  1. Sort by average score (highest first)")
        print("  2. Sort by name (A-Z)")
        print("  3. Sort by student ID")
        print("  4. View class statistics")
        print("  5. Export full report to text file")
        print("  0. Back")

        choice = prompt_int("Choice: ")

        if choice == 0:
            return
        if choice == 1:
            print()
            print_student_table(sort_students(students, "average"),
                                "Sorted by average (highest first):")
            print()
        elif choice == 2:
            print()
            print_student_table(sort_students(students, "name"),
                                "Sorted by name (A-Z):")
            print()
        elif choice == 3:
            print()
            print_student_table(sort_students(students, "id"),
                                "Sorted by student ID:")
            print()
        elif choice == 4:
            print()
            print(format_class_statistics(class_statistics(students)))
            print()
        elif choice == 5:
            print()
            export_report_menu(students)
            print()
        else:
            print("Invalid choice.")


# ----------------------------------------------------------------------
# Menu definition and main loop
# ----------------------------------------------------------------------
MENU = (
    ("1", "Add new student & record 5 subject scores"),
    ("2", "View all registered students"),
    ("3", "Search student by ID or name"),
    ("4", "Update student info or scores"),
    ("5", "Delete a student record"),
    ("6", "Display individual report card"),
    ("7", "Sort students & view class statistics"),
    ("8", "Save and exit"),
)


def show_menu():
    """Print the main menu."""
    print()
    print("=" * 48)
    print("      STUDENT RESULT MANAGEMENT SYSTEM")
    print("=" * 48)
    for key, label in MENU:
        print(f"  {key}. {label}")
    print("=" * 48)


def pause():
    """Wait for the user to press Enter so output remains readable."""
    input("\nPress Enter to continue...")


def main():
    """Run the interactive application loop."""
    students = load_students()
    print(f"Loaded {len(students)} student record(s) from storage.")

    try:
        while True:
            show_menu()
            choice = input("Enter your choice: ").strip()
            print()

            if choice == "1":
                add_student(students)
            elif choice == "2":
                view_students(students)
            elif choice == "3":
                search_student(students)
            elif choice == "4":
                update_student(students)
            elif choice == "5":
                delete_student(students)
            elif choice == "6":
                show_report_card(students)
            elif choice == "7":
                sort_and_statistics(students)
            elif choice == "8":
                break
            else:
                print("Invalid choice. Please enter a number from 1 to 8.")
                continue

            pause()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")

    # Always attempt a safe save on exit (normal exit or Ctrl+C).
    if save_students(students):
        print(f"Saved {len(students)} student record(s).")
    else:
        print("Warning: could not save data to disk.")
    print("Goodbye!")


if __name__ == "__main__":
    main()
