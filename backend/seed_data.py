"""
Inserts a small amount of DEMO/TEST data for Review-2 demonstration.
This is NOT a research dataset — just enough records to show the
end-to-end flow (1 learner, 5 tutors with varied subjects, expertise,
learning preferences and availability).

Run with:
    python3 seed_data.py
(after the backend's tables have been created, e.g. by starting the
API once, or by running the schema.sql script against MySQL directly.)
"""
from app.database import SessionLocal
from app.models.models import Learner, LearnerAvailability, Tutor, TutorAvailability
from app.services.subjects import get_or_create_subjects


def run():
    db = SessionLocal()
    try:
        if db.query(Learner).count() or db.query(Tutor).count():
            print("Demo data already present — skipping seed.")
            return

        learner = Learner(
            name="Ananya Rao",
            email="ananya.rao@example.com",
            learning_preference="Visual",
        )
        learner.subjects = get_or_create_subjects(db, ["Java", "DSA"])
        learner.availability = [LearnerAvailability(slot="Evening")]
        db.add(learner)

        tutors_data = [
            dict(name="Rahul", email="rahul.tutor@example.com", subjects=["Java", "DSA"],
                 expertise_level=4, teaching_preference="Visual", availability=["Evening"]),
            dict(name="Priya", email="priya.tutor@example.com", subjects=["Python", "SQL"],
                 expertise_level=5, teaching_preference="Reading/Writing", availability=["Morning"]),
            dict(name="Karthik", email="karthik.tutor@example.com", subjects=["Java"],
                 expertise_level=3, teaching_preference="Visual", availability=["Evening", "Weekend"]),
            dict(name="Sneha", email="sneha.tutor@example.com", subjects=["DSA", "C++"],
                 expertise_level=4, teaching_preference="Auditory", availability=["Morning", "Evening"]),
            dict(name="Arjun", email="arjun.tutor@example.com", subjects=["Web Development"],
                 expertise_level=2, teaching_preference="Kinesthetic", availability=["Weekend"]),
        ]

        for t in tutors_data:
            tutor = Tutor(
                name=t["name"],
                email=t["email"],
                expertise_level=t["expertise_level"],
                teaching_preference=t["teaching_preference"],
            )
            tutor.subjects = get_or_create_subjects(db, t["subjects"])
            tutor.availability = [TutorAvailability(slot=s) for s in t["availability"]]
            db.add(tutor)

        db.commit()
        print("Seed data inserted: 1 learner, 5 tutors.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
