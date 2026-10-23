from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Learner, ProgressEntry, TutoringSession
from app.schemas.schemas import ProgressCreate, ProgressOut

router = APIRouter(prefix="/api/progress", tags=["learning progress"])

@router.get("/{learner_id}", response_model=list[ProgressOut])
def list_progress(learner_id: int, db: Session = Depends(get_db)):
    if not db.query(Learner).filter_by(id=learner_id).first():
        raise HTTPException(404, "Learner not found")
    return db.query(ProgressEntry).filter_by(learner_id=learner_id).order_by(ProgressEntry.id.desc()).all()

@router.post("", response_model=ProgressOut, status_code=201)
def create_progress(payload: ProgressCreate, db: Session = Depends(get_db)):
    if not db.query(Learner).filter_by(id=payload.learner_id).first():
        raise HTTPException(404, "Learner not found")
    entry = ProgressEntry(learner_id=payload.learner_id, subject=payload.subject.strip(),
                          topic=payload.topic.strip(), notes=payload.notes.strip(),
                          completed=1 if payload.completed else 0)
    db.add(entry); db.commit(); db.refresh(entry); return entry

@router.get("/{learner_id}/summary")
def progress_summary(learner_id: int, db: Session = Depends(get_db)):
    if not db.query(Learner).filter_by(id=learner_id).first():
        raise HTTPException(404, "Learner not found")
    entries = db.query(ProgressEntry).filter_by(learner_id=learner_id).all()
    sessions = db.query(TutoringSession).filter_by(learner_id=learner_id).all()
    return {"learner_id": learner_id, "topics_logged": len(entries),
            "topics_completed": sum(1 for e in entries if e.completed),
            "sessions_total": len(sessions),
            "sessions_completed": sum(1 for s in sessions if s.status == "completed"),
            "subjects": sorted({e.subject for e in entries})}
