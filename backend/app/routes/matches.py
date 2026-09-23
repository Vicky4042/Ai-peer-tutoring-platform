from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Learner, Tutor
from app.schemas.schemas import TutorMatchOut
from app.services.matching import rank_tutors

router = APIRouter(prefix="/api/matches", tags=["matches"])


def _learner_to_dict(learner: Learner) -> dict:
    return {
        "subjects": [s.name for s in learner.subjects],
        "learning_preference": learner.learning_preference,
        "availability": [a.slot for a in learner.availability],
    }


def _tutor_to_dict(tutor: Tutor) -> dict:
    return {
        "tutor_id": tutor.id,
        "name": tutor.name,
        "subjects": [s.name for s in tutor.subjects],
        "expertise_level": tutor.expertise_level,
        "teaching_preference": tutor.teaching_preference,
        "availability": [a.slot for a in tutor.availability],
    }


@router.get("/{learner_id}", response_model=list[TutorMatchOut])
def get_matches(learner_id: int, db: Session = Depends(get_db)):
    learner = db.query(Learner).filter(Learner.id == learner_id).first()
    if not learner:
        raise HTTPException(status_code=404, detail="Learner not found")

    tutors = db.query(Tutor).all()
    if not tutors:
        return []

    ranked = rank_tutors(_learner_to_dict(learner), [_tutor_to_dict(t) for t in tutors])

    return [
        {
            "tutor_id": t["tutor_id"],
            "name": t["name"],
            "subjects": t["subjects"],
            "teaching_preference": t["teaching_preference"],
            "availability": t["availability"],
            "compatibility_score": t["compatibility_score"],
            "breakdown": t["breakdown"],
        }
        for t in ranked
    ]
