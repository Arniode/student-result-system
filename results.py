"""
Result calculation and grading utilities.

Grades are assigned from the average score across the five subjects as follows:

    A -> 70 - 100
    B -> 60 - 69
    C -> 50 - 59
    D -> 45 - 49
    F ->  0 - 44
"""

# The five subjects every student is graded on.
SUBJECTS = ("Mathematics", "English", "Physics", "Chemistry", "Biology")

# Valid score range for a single subject.
MIN_SCORE = 0
MAX_SCORE = 100


def calculate_total(scores):
    """Return the sum of all subject scores."""
    if not scores:
        return 0
    return sum(scores.values())


def calculate_average(scores):
    """Return the average score across the recorded subjects."""
    if not scores:
        return 0.0
    return calculate_total(scores) / len(scores)


def assign_grade(average):
    """Map an average score to its corresponding letter grade."""
    if average is None:
        return None
    if average >= 70:
        return "A"
    if average >= 60:
        return "B"
    if average >= 50:
        return "C"
    if average >= 45:
        return "D"
    return "F"


def compute_results(scores):
    """Compute and return ``(total, average, grade)`` for a score set.

    When no scores are present the total and average default to zero and the
    grade is ``None``.
    """
    if not scores:
        return 0, 0.0, None

    total = calculate_total(scores)
    average = round(calculate_average(scores), 2)
    grade = assign_grade(average)
    return total, average, grade
