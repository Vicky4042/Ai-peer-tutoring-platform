from sqlalchemy.orm import Session
from app.models.models import Subject


def get_or_create_subjects(db: Session, names: list[str]) -> list[Subject]:
    """
    Look up each subject name; create it if it doesn't exist yet.
    Keeps the `subjects` reference table small and reusable across
    learners and tutors instead of duplicating free-text subject strings.
    """
    result = []
    for raw_name in names:
        name = raw_name.strip()
        if not name:
            continue
        subject = db.query(Subject).filter(Subject.name.ilike(name)).first()
        if not subject:
            subject = Subject(name=name)
            db.add(subject)
            db.flush()  # get subject.id without committing yet
        result.append(subject)
    return result
