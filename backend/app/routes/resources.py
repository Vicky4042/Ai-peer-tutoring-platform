from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import LearningResource
from app.schemas.schemas import ResourceCreate, ResourceOut

router = APIRouter(prefix="/api/resources", tags=["learning materials"])

@router.get("", response_model=list[ResourceOut])
def list_resources(subject: str | None = None, q: str | None = None,
                   resource_type: str | None = None, db: Session = Depends(get_db)):
    query = db.query(LearningResource)
    if subject and subject.strip() and subject.lower() != "all":
        query = query.filter(LearningResource.subject.ilike(f"%{subject.strip()}%"))
    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter((LearningResource.title.ilike(term)) |
                             (LearningResource.description.ilike(term)) |
                             (LearningResource.subject.ilike(term)))
    if resource_type and resource_type.lower() != "all":
        query = query.filter(LearningResource.resource_type.ilike(resource_type))
    return query.order_by(LearningResource.subject, LearningResource.title).all()

@router.post("", response_model=ResourceOut, status_code=201)
def create_resource(payload: ResourceCreate, db: Session = Depends(get_db)):
    resource = LearningResource(**payload.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource
