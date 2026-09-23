from typing import List
from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------
# Learner schemas
# ---------------------------------------------------------------
class LearnerCreate(BaseModel):
    name: str
    email: EmailStr
    subjects: List[str] = Field(..., description="Subjects/topics the learner needs help with")
    learning_preference: str
    availability: List[str] = Field(..., description="e.g. ['Morning', 'Evening']")


class LearnerOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    subjects: List[str]
    learning_preference: str
    availability: List[str]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------
# Tutor schemas
# ---------------------------------------------------------------
class TutorCreate(BaseModel):
    name: str
    email: EmailStr
    subjects: List[str] = Field(..., description="Subjects/skills the tutor teaches")
    expertise_level: int = Field(..., ge=1, le=5, description="1 (beginner-friendly) - 5 (highly experienced)")
    teaching_preference: str
    availability: List[str]


class TutorOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    subjects: List[str]
    expertise_level: int
    teaching_preference: str
    availability: List[str]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------
# Match / recommendation schemas
# ---------------------------------------------------------------
class MatchBreakdown(BaseModel):
    subject_score: float
    expertise_score: float
    preference_score: float
    availability_score: float


class TutorMatchOut(BaseModel):
    tutor_id: int
    name: str
    subjects: List[str]
    teaching_preference: str
    availability: List[str]
    compatibility_score: float
    breakdown: MatchBreakdown
