"""
End-to-end test of GET /api/matches/{learner_id} using an in-memory SQLite database
(no MySQL needed). Skipped automatically if FastAPI/SQLAlchemy/httpx are not installed.
"""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")
pytest.importorskip("httpx")
pytest.importorskip("pymysql")  # app.database creates a MySQL engine object at import time

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.ml import model_loader
from app.models.models import Learner, LearnerAvailability, Tutor, TutorAvailability
from app.routes import matches
from app.services.subjects import get_or_create_subjects


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.delenv("MATCHING_MODE", raising=False)
    model_loader.reset_model_cache()
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    db = Session()
    learner = Learner(name="Ananya", email="a@example.com", learning_preference="Visual")
    learner.subjects = get_or_create_subjects(db, ["Java", "DSA"])
    learner.availability = [LearnerAvailability(slot="Evening")]
    db.add(learner)
    for name, subjects, exp, pref, slots in [
        ("Rahul", ["Java", "DSA"], 4, "Visual", ["Evening"]),
        ("Priya", ["Python", "SQL"], 5, "Reading/Writing", ["Morning"]),
        ("Karthik", ["Java"], 3, "Visual", ["Evening", "Weekend"]),
    ]:
        t = Tutor(name=name, email=f"{name.lower()}@example.com", expertise_level=exp, teaching_preference=pref)
        t.subjects = get_or_create_subjects(db, subjects)
        t.availability = [TutorAvailability(slot=s) for s in slots]
        db.add(t)
    db.commit()
    db.close()

    def override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app = FastAPI()
    app.include_router(matches.router)
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    model_loader.reset_model_cache()


def test_matches_endpoint_returns_ml_ranked_eligible_tutors(client):
    res = client.get("/api/matches/1")
    assert res.status_code == 200
    body = res.json()
    names = [m["name"] for m in body]
    assert set(names) == {"Rahul", "Karthik"}  # Priya teaches neither requested subject
    probs = [m["ml_match_probability"] for m in body]
    assert probs == sorted(probs, reverse=True)
    for m in body:
        assert m["scoring_method"] == "ml"
        assert m["fallback_reason"] is None
        assert m["match_score"] == pytest.approx(m["ml_match_probability"] * 100, abs=0.01)
        assert "compatibility_score" in m and "breakdown" in m


def test_matches_endpoint_labels_fallback(client, monkeypatch, tmp_path):
    monkeypatch.setattr(model_loader, "MODEL_PATH", tmp_path / "missing.joblib")
    model_loader.reset_model_cache()
    body = client.get("/api/matches/1").json()
    assert body and all(m["scoring_method"] == "fallback" and m["ml_match_probability"] is None for m in body)


def test_matches_endpoint_unknown_learner_404(client):
    assert client.get("/api/matches/999").status_code == 404
