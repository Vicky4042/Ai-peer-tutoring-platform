from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Learner, LearnerAvailability
from app.schemas.schemas import LearnerCreate, LearnerOut
from app.services.subjects import get_or_create_subjects

router = APIRouter(prefix="/api/learners", tags=["learners"])


def _to_out(learner: Learner) -> dict:
    return {
        "id": learner.id,
        "name": learner.name,
        "email": learner.email,
        "subjects": [s.name for s in learner.subjects],
        "learning_preference": learner.learning_preference,
        "availability": [a.slot for a in learner.availability],
    }


@router.post("", response_model=LearnerOut, status_code=201)
def create_learner(payload: LearnerCreate, db: Session = Depends(get_db)):
    existing = db.query(Learner).filter(Learner.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="A learner with this email already exists")

    learner = Learner(
        name=payload.name,
        email=payload.email,
        learning_preference=payload.learning_preference,
    )
    learner.subjects = get_or_create_subjects(db, payload.subjects)
    learner.availability = [LearnerAvailability(slot=slot) for slot in payload.availability]

    db.add(learner)
    db.commit()
    db.refresh(learner)
    return _to_out(learner)


@router.get("/{learner_id}", response_model=LearnerOut)
def get_learner(learner_id: int, db: Session = Depends(get_db)):
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")
    return _to_out(learner)
