from typing import List, Literal, Optional
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
    matched_subjects: List[str] = Field(default_factory=list)
    teaching_preference: str
    availability: List[str]

    # Original compatibility score (0-100)
    compatibility_score: float
    breakdown: MatchBreakdown

    # Score used for ranking and display (0-100)
    match_score: float
    scoring_method: Literal["ml", "fallback"]

    # ML prediction probability (0-1)
    ml_match_probability: Optional[float] = None

    # Reason for using fallback, if applicable
    fallback_reason: Optional[str] = None


# ---------------------------------------------------------------
# Learning resources and peer-learning workflow
# ---------------------------------------------------------------
from datetime import datetime
from pydantic import HttpUrl, field_validator

class ResourceCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    subject: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=4000)
    resource_type: str = Field(default="Tutorial", max_length=40)
    url: str = Field(min_length=8, max_length=1000)

    @field_validator("url")
    @classmethod
    def valid_http_url(cls, value: str) -> str:
        if not value.startswith(("https://", "http://")):
            raise ValueError("URL must start with http:// or https://")
        return value

class ResourceOut(BaseModel):
    id: int
    title: str
    subject: str
    description: str
    resource_type: str
    url: str
    class Config:
        from_attributes = True

class SessionCreate(BaseModel):
    learner_id: int
    tutor_id: int
    subject: str = Field(min_length=1, max_length=100)
    topic: str = Field(min_length=2, max_length=200)
    scheduled_at: datetime
    message: str = Field(default="", max_length=2000)

class SessionStatusUpdate(BaseModel):
    status: Literal["accepted", "rejected", "completed", "cancelled"]
    tutor_response: str = Field(default="", max_length=2000)

class SessionOut(BaseModel):
    id: int
    learner_id: int
    tutor_id: int
    subject: str
    topic: str
    scheduled_at: datetime
    message: str
    status: str
    tutor_response: str
    class Config:
        from_attributes = True

class ProgressCreate(BaseModel):
    learner_id: int
    subject: str = Field(min_length=1, max_length=100)
    topic: str = Field(min_length=2, max_length=200)
    notes: str = Field(default="", max_length=2000)
    completed: bool = False

class ProgressOut(BaseModel):
    id: int
    learner_id: int
    subject: str
    topic: str
    notes: str
    completed: int
    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    learner_id: int
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=2000)

class FeedbackOut(BaseModel):
    id: int
    session_id: int
    learner_id: int
    rating: int
    comment: str
    class Config:
        from_attributes = True
