from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Learner, Tutor, TutoringSession, SessionFeedback
from app.schemas.schemas import SessionCreate, SessionOut, SessionStatusUpdate, FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/api/sessions", tags=["tutoring sessions"])
_ALLOWED = {"pending": {"accepted", "rejected", "cancelled"},
            "accepted": {"completed", "cancelled"},
            "rejected": set(), "completed": set(), "cancelled": set()}

@router.post("", response_model=SessionOut, status_code=201)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    learner = db.query(Learner).filter_by(id=payload.learner_id).first()
    tutor = db.query(Tutor).filter_by(id=payload.tutor_id).first()
    if not learner: raise HTTPException(404, "Learner not found")
    if not tutor: raise HTTPException(404, "Tutor not found")
    now = datetime.now(payload.scheduled_at.tzinfo) if payload.scheduled_at.tzinfo else datetime.now()
    if payload.scheduled_at < now:
        raise HTTPException(422, "Session date/time must be in the future")
    if payload.subject.lower() not in {s.name.lower() for s in learner.subjects}:
        raise HTTPException(422, "Session subject must be one of the learner's subjects")
    if payload.subject.lower() not in {s.name.lower() for s in tutor.subjects}:
        raise HTTPException(422, "Tutor does not teach this subject")
    duplicate = db.query(TutoringSession).filter(
        TutoringSession.learner_id == payload.learner_id,
        TutoringSession.tutor_id == payload.tutor_id,
        TutoringSession.subject == payload.subject,
        TutoringSession.scheduled_at == payload.scheduled_at,
        TutoringSession.status.in_(["pending", "accepted"])).first()
    if duplicate: raise HTTPException(409, "A request for this tutor and time already exists")
    item = TutoringSession(**payload.model_dump(), status="pending")
    db.add(item); db.commit(); db.refresh(item); return item

@router.get("", response_model=list[SessionOut])
def list_sessions(learner_id: int | None = None, tutor_id: int | None = None,
                  status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(TutoringSession)
    if learner_id is not None: query = query.filter_by(learner_id=learner_id)
    if tutor_id is not None: query = query.filter_by(tutor_id=tutor_id)
    if status: query = query.filter_by(status=status.lower())
    return query.order_by(TutoringSession.scheduled_at.desc()).all()

@router.patch("/{session_id}", response_model=SessionOut)
def update_session(session_id: int, payload: SessionStatusUpdate, db: Session = Depends(get_db)):
    item = db.query(TutoringSession).filter_by(id=session_id).first()
    if not item: raise HTTPException(404, "Session not found")
    if payload.status not in _ALLOWED.get(item.status, set()):
        raise HTTPException(409, f"Cannot change session from {item.status} to {payload.status}")
    item.status = payload.status
    item.tutor_response = payload.tutor_response
    db.commit(); db.refresh(item); return item

@router.post("/{session_id}/feedback", response_model=FeedbackOut, status_code=201)
def add_feedback(session_id: int, payload: FeedbackCreate, db: Session = Depends(get_db)):
    item = db.query(TutoringSession).filter_by(id=session_id).first()
    if not item: raise HTTPException(404, "Session not found")
    if item.learner_id != payload.learner_id: raise HTTPException(403, "Feedback must be submitted by the session learner")
    if item.status != "completed": raise HTTPException(409, "Feedback is available after session completion")
    if db.query(SessionFeedback).filter_by(session_id=session_id).first():
        raise HTTPException(409, "Feedback has already been submitted")
    feedback = SessionFeedback(session_id=session_id, learner_id=payload.learner_id,
                               rating=payload.rating, comment=payload.comment)
    db.add(feedback); db.commit(); db.refresh(feedback); return feedback
