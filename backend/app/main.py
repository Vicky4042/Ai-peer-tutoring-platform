from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routes import learners, tutors, matches

# Creates tables if they don't exist yet. For Review-2 this is fine;
# a migration tool (e.g. Alembic) is left for Part 2 / future work.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Based Peer Tutoring Matching Platform — API",
    description="Review-2 backend: learner/tutor profiles and compatibility-based tutor matching.",
    version="0.1.0-review2",
)

# Allow the Flutter app (emulator/device/web) to call the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(learners.router)
app.include_router(tutors.router)
app.include_router(matches.router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "peer-tutoring-matching-api",
        "stage": "Review-2 (approx. 50% implementation)",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
