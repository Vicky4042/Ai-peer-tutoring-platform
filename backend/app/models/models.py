from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base

# ---------------------------------------------------------------
# Association tables (many-to-many)
# ---------------------------------------------------------------
learner_subjects = None  # defined below via Table for clarity

from sqlalchemy import Table  # noqa: E402

learner_subjects = Table(
    "learner_subjects",
    Base.metadata,
    Column("learner_id", Integer, ForeignKey("learners.id", ondelete="CASCADE"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True),
)

tutor_subjects = Table(
    "tutor_subjects",
    Base.metadata,
    Column("tutor_id", Integer, ForeignKey("tutors.id", ondelete="CASCADE"), primary_key=True),
    Column("subject_id", Integer, ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True),
)


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)


class Learner(Base):
    __tablename__ = "learners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    learning_preference = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    subjects = relationship("Subject", secondary=learner_subjects, backref="learners")
    availability = relationship("LearnerAvailability", back_populates="learner", cascade="all, delete-orphan")


class LearnerAvailability(Base):
    __tablename__ = "learner_availability"

    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    slot = Column(String(50), nullable=False)

    learner = relationship("Learner", back_populates="availability")


class Tutor(Base):
    __tablename__ = "tutors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    expertise_level = Column(Integer, nullable=False, default=1)
    teaching_preference = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    subjects = relationship("Subject", secondary=tutor_subjects, backref="tutors")
    availability = relationship("TutorAvailability", back_populates="tutor", cascade="all, delete-orphan")


class TutorAvailability(Base):
    __tablename__ = "tutor_availability"

    id = Column(Integer, primary_key=True, index=True)
    tutor_id = Column(Integer, ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False)
    slot = Column(String(50), nullable=False)

    tutor = relationship("Tutor", back_populates="availability")


# ---------------------------------------------------------------
# Learning resources, tutoring sessions, progress and feedback
# ---------------------------------------------------------------
from sqlalchemy import Text, DateTime, Float, UniqueConstraint

class LearningResource(Base):
    __tablename__ = "learning_resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False, default="")
    resource_type = Column(String(40), nullable=False, default="Tutorial")
    url = Column(String(1000), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class TutoringSession(Base):
    __tablename__ = "tutoring_sessions"
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True)
    tutor_id = Column(Integer, ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(100), nullable=False)
    topic = Column(String(200), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    message = Column(Text, nullable=False, default="")
    status = Column(String(20), nullable=False, default="pending", index=True)
    tutor_response = Column(Text, nullable=False, default="")
    created_at = Column(TIMESTAMP, server_default=func.now())
    learner = relationship("Learner")
    tutor = relationship("Tutor")
    feedback = relationship("SessionFeedback", back_populates="session", uselist=False, cascade="all, delete-orphan")


class ProgressEntry(Base):
    __tablename__ = "progress_entries"
    id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learners.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(100), nullable=False)
    topic = Column(String(200), nullable=False)
    notes = Column(Text, nullable=False, default="")
    completed = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    learner = relationship("Learner")


class SessionFeedback(Base):
    __tablename__ = "session_feedback"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("tutoring_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    learner_id = Column(Integer, ForeignKey("learners.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=False, default="")
    created_at = Column(TIMESTAMP, server_default=func.now())
    session = relationship("TutoringSession", back_populates="feedback")
    learner = relationship("Learner")
