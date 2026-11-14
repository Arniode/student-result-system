"""
Web interface for the Student Result Management System.

A thin Flask layer over the existing student/results/storage/reports modules
so the same application can be hosted as a web service (e.g. on Render).

Local run:  python app.py
Production: gunicorn app:app --bind 0.0.0.0:$PORT
"""

import csv
import io
import os
import re
from datetime import datetime

from flask import (Flask, Response, flash, redirect, render_template,
                   request, url_for)

from results import SUBJECTS, MIN_SCORE, MAX_SCORE
from reports import (class_statistics, format_class_statistics,
                     format_report_card, sort_students)
from storage import load_students, save_students
from student import Student

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "srms-demo-secret")


def _initials(name):
    """Return up to two initials (e.g. 'Jane Doe' -> 'JD')."""
    parts = name.split()
    return "".join(p[0].upper() for p in parts[:2]) or "?"


def _grade_class(grade):
    """Map a grade letter to a CSS modifier class for colour-coding."""
    mapping = {"A": "grade-a", "B": "grade-b", "C": "grade-c",
               "D": "grade-d", "F": "grade-f"}
    return mapping.get((grade or "").upper(), "grade-na")


app.add_template_filter(_initials, "initials")
app.add_template_filter(_grade_class, "grade_class")

ID_PATTERN = re.compile(r"^[A-Za-z]{1,5}\d{1,6}$")


def find_by_id(students, sid):
    """Return the first student matching the given ID (case-insensitive)."""
    sid = sid.lower()
    for student in students:
        if student.student_id.lower() == sid:
            return student
    return None


def valid_dob(value):
    """Return True if the value is a valid YYYY-MM-DD date."""
    try:
        datetime.strptime(value, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def parse_scores(form):
    """Extract and validate the five subject scores from a request form."""
    scores = {}
    for subject in SUBJECTS:
        raw = form.get(subject, "").strip()
        if raw == "":
            return None, f"Please enter a score for {subject}."
        try:
            value = float(raw)
        except ValueError:
            return None, f"{subject} score must be a number."
        if value < MIN_SCORE or value > MAX_SCORE:
            return None, (f"{subject} score must be between "
                          f"{MIN_SCORE} and {MAX_SCORE}.")
        scores[subject] = value
    return scores, None


@app.route("/")
def index():
    students = load_students()
    stats = class_statistics(students) if students else None
    return render_template("index.html", students=students, stats=stats)


@app.route("/add", methods=["GET", "POST"])
def add_student_page():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        full_name = request.form.get("full_name", "").strip()
        class_form = request.form.get("class_form", "").strip()
        gender = request.form.get("gender", "").strip()
        dob = request.form.get("dob", "").strip()

        errors = []
        if not ID_PATTERN.fullmatch(student_id):
            errors.append("Invalid Student ID (1-5 letters then 1-6 digits, "
                          "e.g. S001).")
        if not full_name:
            errors.append("Full name is required.")
        if not class_form:
            errors.append("Class/Form is required.")
        if not gender:
            errors.append("Gender is required.")
        if not valid_dob(dob):
            errors.append("Date of birth must be in YYYY-MM-DD format.")

        students = load_students()
        if student_id and find_by_id(students, student_id):
            errors.append("A student with that ID already exists.")

        scores, score_error = parse_scores(request.form)
        if score_error:
            errors.append(score_error)

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "student_form.html", student=None, values=request.form,
                subjects=SUBJECTS, min_score=MIN_SCORE, max_score=MAX_SCORE)

        student = Student(student_id, full_name, class_form, gender, dob,
                          scores=scores)
        students.append(student)
        if save_students(students):
            flash(f"Student '{full_name}' added successfully.", "success")
            return redirect(url_for("index"))
        flash("Could not save data to disk.", "error")

    return render_template("student_form.html", student=None, values={},
                           subjects=SUBJECTS, min_score=MIN_SCORE,
                           max_score=MAX_SCORE)


@app.route("/student/<sid>")
def student_detail(sid):
    student = find_by_id(load_students(), sid)
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("index"))
    return render_template("student_detail.html", student=student,
                           report=format_report_card(student))


@app.route("/student/<sid>/edit", methods=["GET", "POST"])
def edit_student(sid):
    students = load_students()
    student = find_by_id(students, sid)
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip() or student.full_name
        class_form = request.form.get("class_form", "").strip() or student.class_form
        gender = request.form.get("gender", "").strip() or student.gender
        dob = request.form.get("dob", "").strip() or student.dob

        errors = []
        if not valid_dob(dob):
            errors.append("Date of birth must be in YYYY-MM-DD format.")

        scores, score_error = parse_scores(request.form)
        if score_error:
            errors.append(score_error)

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template(
                "student_form.html", student=student, values=request.form,
                subjects=SUBJECTS, min_score=MIN_SCORE, max_score=MAX_SCORE)

        student.update_details(full_name=full_name, class_form=class_form,
                               gender=gender, dob=dob)
        student.update_scores(scores)
        if save_students(students):
            flash(f"'{student.full_name}' updated successfully.", "success")
            return redirect(url_for("student_detail", sid=student.student_id))
        flash("Could not save data to disk.", "error")

    values = {
        "full_name": student.full_name,
        "class_form": student.class_form,
        "gender": student.gender,
        "dob": student.dob,
    }
    for subject in SUBJECTS:
        values[subject] = student.scores.get(subject, "")
    return render_template("student_form.html", student=student, values=values,
                           subjects=SUBJECTS, min_score=MIN_SCORE,
                           max_score=MAX_SCORE)


@app.route("/student/<sid>/delete", methods=["POST"])
def delete_student(sid):
    students = load_students()
    student = find_by_id(students, sid)
    if student is None:
        flash("Student not found.", "error")
        return redirect(url_for("index"))
    students.remove(student)
    if save_students(students):
        flash(f"'{student.full_name}' deleted.", "success")
    else:
        flash("Could not save data to disk.", "error")
    return redirect(url_for("index"))


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return redirect(url_for("index"))
    ql = query.lower()
    students = load_students()
    results = [s for s in students
               if ql in s.full_name.lower() or ql in s.student_id.lower()]
    return render_template("search.html", query=query, results=results)


@app.route("/statistics")
def statistics():
    students = load_students()
    if not students:
        flash("No students registered yet.", "error")
        return redirect(url_for("index"))
    stats = class_statistics(students)
    ranked = sort_students(students, "average")
    grade_counts = {}
    for student in students:
        grade = student.grade or "N/A"
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    return render_template("statistics.html", stats=stats, ranked=ranked,
                           grade_counts=grade_counts)


@app.route("/wheel")
def wheel():
    students = load_students()
    wheel_students = [
        {
            "first": s.full_name.split()[0],
            "full_name": s.full_name,
            "student_id": s.student_id,
            "average": round(s.average, 1) if s.average is not None else None,
            "grade": s.grade or "N/A",
            "initials": _initials(s.full_name),
        }
        for s in students
    ]
    return render_template("wheel.html", students=students,
                           wheel_students=wheel_students)


@app.route("/export.csv")
def export_csv():
    students = load_students()
    output = io.StringIO()
    writer = csv.writer(output)
    header = ["Student ID", "Full Name", "Class/Form", "Gender", "DOB",
              *SUBJECTS, "Total", "Average", "Grade", "Date Added"]
    writer.writerow(header)
    for student in students:
        writer.writerow([
            student.student_id, student.full_name, student.class_form,
            student.gender, student.dob,
            *[student.scores.get(s, "") for s in SUBJECTS],
            student.total, student.average,
            student.grade if student.grade else "",
            student.date_added,
        ])
    return Response(
        output.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=class_report.csv"})


@app.route("/export.txt")
def export_text():
    students = load_students()
    if not students:
        flash("No student records to export.", "error")
        return redirect(url_for("index"))

    ranked = sort_students(students, "average")
    stats = class_statistics(students)
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
            f"{student.average:>8}{grade:>8}")
    lines.append("=" * 62)

    return Response(
        "\n".join(lines) + "\n", mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=class_report.txt"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
