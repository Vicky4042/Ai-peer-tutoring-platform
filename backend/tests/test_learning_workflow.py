"""Integration tests for the peer-learning workflow using an isolated SQLite database."""
import pytest
pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")
pytest.importorskip("httpx")


from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.routes import learners, tutors, resources, sessions, progress
from app.models.models import LearningResource, Learner, Tutor, TutoringSession, ProgressEntry
from app.services.subjects import get_or_create_subjects

@pytest.fixture()
def client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = Session()
    learner = Learner(name="Test Learner", email="learner@test.example", learning_preference="Visual")
    learner.subjects = get_or_create_subjects(db, ["Python", "Java"])
    tutor = Tutor(name="Test Tutor", email="tutor@test.example", expertise_level=4, teaching_preference="Visual")
    tutor.subjects = get_or_create_subjects(db, ["Python"])
    db.add_all([learner, tutor]); db.commit()
    learner_id, tutor_id = learner.id, tutor.id
    db.add(LearningResource(title="Python Docs", subject="Python", description="Official docs",
                            resource_type="Documentation", url="https://docs.python.org/3/"))
    db.commit(); db.close()
    def override_db():
        session = Session()
        try: yield session
        finally: session.close()
    app = FastAPI()
    for router in (learners.router, tutors.router, resources.router, sessions.router, progress.router):
        app.include_router(router)
    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client, learner_id, tutor_id
    Base.metadata.drop_all(engine)
    engine.dispose()

def test_resources_search_and_filter(client):
    c, _, _ = client
    response = c.get("/api/resources", params={"subject": "Python", "q": "docs"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Python Docs"

def test_session_lifecycle_and_feedback(client):
    c, learner_id, tutor_id = client
    created = c.post("/api/sessions", json={
        "learner_id": learner_id, "tutor_id": tutor_id, "subject": "Python", "topic": "Functions",
        "scheduled_at": (datetime.now().astimezone() + timedelta(days=2)).isoformat(), "message": "Please help"
    })
    assert created.status_code == 201, created.text
    session_id = created.json()["id"]
    assert c.patch(f"/api/sessions/{session_id}", json={"status": "completed"}).status_code == 409
    assert c.patch(f"/api/sessions/{session_id}", json={"status": "accepted"}).status_code == 200
    assert c.patch(f"/api/sessions/{session_id}", json={"status": "completed"}).status_code == 200
    feedback = c.post(f"/api/sessions/{session_id}/feedback", json={"learner_id": learner_id, "rating": 5, "comment": "Helpful"})
    assert feedback.status_code == 201, feedback.text
    assert c.post(f"/api/sessions/{session_id}/feedback", json={"learner_id": learner_id, "rating": 5}).status_code == 409

def test_duplicate_active_session_request_is_rejected(client):
    c, learner_id, tutor_id = client
    payload = {"learner_id": learner_id, "tutor_id": tutor_id, "subject": "Python", "topic": "Functions",
               "scheduled_at": (datetime.now() + timedelta(days=2)).isoformat()}
    assert c.post("/api/sessions", json=payload).status_code == 201
    assert c.post("/api/sessions", json=payload).status_code == 409

def test_progress_entry_and_summary(client):
    c, learner_id, _ = client
    response = c.post("/api/progress", json={"learner_id": learner_id, "subject": "Python",
                            "topic": "Lists", "notes": "Practice indexing", "completed": True})
    assert response.status_code == 201
    summary = c.get(f"/api/progress/{learner_id}/summary")
    assert summary.status_code == 200
    assert summary.json()["topics_completed"] == 1
