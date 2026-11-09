"""
Data model for a single student.

This module defines the :class:`Student` class used across the system. The
class holds basic biographical information, a dictionary of subject scores and
the computed results (total, average and grade).
"""

from datetime import datetime

from results import compute_results


class Student:
    """Represent a student and their academic record.

    Attributes:
        student_id (str):  Unique identifier for the student.
        full_name (str):   Full name of the student.
        class_form (str):  Class/form the student belongs to.
        gender (str):      Gender of the student.
        dob (str):         Date of birth in ISO format (YYYY-MM-DD).
        scores (dict):     Mapping of subject name -> score.
        total (float):     Sum of all subject scores.
        average (float):   Average score across the recorded subjects.
        grade (str):       Letter grade derived from the average.
        date_added (str):  ISO timestamp when the record was created.
    """

    def __init__(self, student_id, full_name, class_form, gender, dob,
                 scores=None, date_added=None):
        self.student_id = str(student_id).strip()
        self.full_name = full_name.strip()
        self.class_form = class_form.strip()
        self.gender = gender.strip()
        self.dob = dob.strip()

        self.scores = dict(scores) if scores else {}

        # Stamp new records with the current time; keep an existing timestamp
        # when loading previously saved data.
        self.date_added = (
            date_added.strip() if date_added else datetime.now().isoformat()
        )

        # Compute the results immediately so the object is always consistent.
        self.total, self.average, self.grade = compute_results(self.scores)

    # ------------------------------------------------------------------
    # Result computation
    # ------------------------------------------------------------------
    def compute_results(self):
        """Recompute total, average and grade from the current scores."""
        self.total, self.average, self.grade = compute_results(self.scores)
        return self.total, self.average, self.grade

    # ------------------------------------------------------------------
    # Update helpers
    # ------------------------------------------------------------------
    def update_details(self, full_name=None, class_form=None, gender=None,
                       dob=None):
        """Update biographical details. Only non-None values are applied."""
        if full_name is not None:
            self.full_name = full_name.strip()
        if class_form is not None:
            self.class_form = class_form.strip()
        if gender is not None:
            self.gender = gender.strip()
        if dob is not None:
            self.dob = dob.strip()

    def update_scores(self, scores):
        """Replace the entire score set and recompute results."""
        self.scores = dict(scores)
        self.compute_results()

    def update_single_score(self, subject, score):
        """Update a single subject score and recompute results."""
        self.scores[subject] = score
        self.compute_results()

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------
    def to_dict(self):
        """Return a plain dictionary suitable for JSON serialisation."""
        return {
            "student_id": self.student_id,
            "full_name": self.full_name,
            "class_form": self.class_form,
            "gender": self.gender,
            "dob": self.dob,
            "scores": self.scores,
            "total": self.total,
            "average": self.average,
            "grade": self.grade,
            "date_added": self.date_added,
        }

    @classmethod
    def from_dict(cls, data):
        """Build a :class:`Student` instance from a dictionary."""
        return cls(
            student_id=data.get("student_id", ""),
            full_name=data.get("full_name", ""),
            class_form=data.get("class_form", ""),
            gender=data.get("gender", ""),
            dob=data.get("dob", ""),
            scores=data.get("scores", {}),
            date_added=data.get("date_added"),
        )

    def __str__(self):
        grade = self.grade if self.grade else "N/A"
        return (f"{self.student_id} | {self.full_name} | {self.class_form} "
                f"| Avg: {self.average} | Grade: {grade}")
