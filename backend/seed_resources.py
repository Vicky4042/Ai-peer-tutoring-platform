"""Idempotently seed a small set of reputable free learning resources."""
from app.database import Base, SessionLocal, engine
from app.models.models import LearningResource

RESOURCES = [
    ("Python Tutorial", "Python", "Official Python tutorial and language reference.", "Documentation", "https://docs.python.org/3/tutorial/"),
    ("Java Tutorials", "Java", "Official Java learning trails and language guides.", "Documentation", "https://dev.java/learn/"),
    ("Git Book", "Git", "Free online book explaining Git fundamentals and workflows.", "Book", "https://git-scm.com/book/en/v2"),
    ("MDN JavaScript Guide", "JavaScript", "JavaScript language guide with examples.", "Documentation", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"),
    ("SQL Tutorial", "SQL", "Interactive SQL lessons and practice.", "Practice", "https://www.sqlbolt.com/"),
    ("Flutter Documentation", "Flutter", "Official Flutter learning and widget documentation.", "Documentation", "https://docs.flutter.dev/"),
    ("FastAPI Tutorial", "Python", "Official FastAPI tutorial and API examples.", "Documentation", "https://fastapi.tiangolo.com/tutorial/"),
    ("Khan Academy Computer Science", "Computer Science", "Free computing concepts and programming content.", "Course", "https://www.khanacademy.org/computing"),
    ("freeCodeCamp", "Web Development", "Free coding courses and practice projects.", "Course", "https://www.freecodecamp.org/learn/"),
    ("GeeksforGeeks DSA", "Data Structures", "Data structures and algorithms explanations and practice.", "Practice", "https://www.geeksforgeeks.org/data-structures/"),
]

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = {r.url for r in db.query(LearningResource.url).all()}
        added = 0
        for title, subject, description, kind, url in RESOURCES:
            if url not in existing:
                db.add(LearningResource(title=title, subject=subject, description=description,
                                        resource_type=kind, url=url))
                existing.add(url); added += 1
        db.commit()
        print(f"Seed complete: {added} resources added; {len(existing)} unique URLs available.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
