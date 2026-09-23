from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Tutor, TutorAvailability
from app.schemas.schemas import TutorCreate, TutorOut
from app.services.subjects import get_or_create_subjects

router = APIRouter(prefix="/api/tutors", tags=["tutors"])


def _to_out(tutor: Tutor) -> dict:
    return {
        "id": tutor.id,
        "name": tutor.name,
        "email": tutor.email,
        "subjects": [s.name for s in tutor.subjects],
        "expertise_level": tutor.expertise_level,
        "teaching_preference": tutor.teaching_preference,
        "availability": [a.slot for a in tutor.availability],
    }


@router.post("", response_model=TutorOut, status_code=201)
def create_tutor(payload: TutorCreate, db: Session = Depends(get_db)):
    existing = db.query(Tutor).filter(Tutor.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="A tutor with this email already exists")

    tutor = Tutor(
        name=payload.name,
        email=payload.email,
        expertise_level=payload.expertise_level,
        teaching_preference=payload.teaching_preference,
    )
    tutor.subjects = get_or_create_subjects(db, payload.subjects)
    tutor.availability = [TutorAvailability(slot=slot) for slot in payload.availability]

    db.add(tutor)
    db.commit()
    db.refresh(tutor)
    return _to_out(tutor)


@router.get("", response_model=list[TutorOut])
def list_tutors(db: Session = Depends(get_db)):
    tutors = db.query(Tutor).all()
    return [_to_out(t) for t in tutors]
