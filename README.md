# AI-Based Peer Tutoring Matching Platform

**Presidency University, Bengaluru — CSE7102 Mini Project — Review-2 (26-09-2026)**

Team: Vikas V (20231CSE0624), Shubhamkar Dash (20231CSE0611), Vikas A (20231CSE0547)
Guide: Dr. Balakrishnan Raju

## Review-2 scope

This repository contains the **Review-2 implementation (~50% of the final project)**:
a working end-to-end MVP that demonstrates

```
Flutter (profile forms) → FastAPI → MySQL → compatibility matching → ranked
tutor recommendations → Flutter (recommendation screen)
```

Session management, feedback, advanced ML, authentication, deployment and
other features are **intentionally out of scope for Review-2** — see
"Future Work" below.

## Repository structure

```
Ai-peer-tutoring-platform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entrypoint
│   │   ├── database.py          # SQLAlchemy engine/session
│   │   ├── models/models.py     # ORM models
│   │   ├── schemas/schemas.py   # Pydantic request/response schemas
│   │   ├── routes/              # learners.py, tutors.py, matches.py
│   │   └── services/
│   │       ├── matching.py      # compatibility scoring (pure Python)
│   │       └── subjects.py      # get-or-create helper for Subject rows
│   ├── sql/schema.sql           # MySQL schema
│   ├── seed_data.py             # inserts 1 learner + 5 demo tutors
│   ├── test_matching.py         # standalone tests for matching.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/                    # Flutter app
│   ├── pubspec.yaml
│   └── lib/
│       ├── main.dart
│       ├── models/               # Learner, Tutor, TutorMatch
│       ├── services/api_service.dart
│       └── screens/              # Home, LearnerProfile, TutorProfile, Recommendation
└── README.md
```

## How the matching works (Review-2)

`backend/app/services/matching.py` computes a **weighted compatibility
score (0–100)**, not a trained ML model:

| Factor                     | Weight |
|-----------------------------|--------|
| Subject/skill compatibility | 40%    |
| Tutor expertise             | 25%    |
| Learning preference match   | 20%    |
| Availability overlap        | 15%    |

Tutors are sorted by this score, highest first. The exact ML/recommendation
algorithm is **not yet finalized** — see Future Work.

## Setup & run instructions

### 1. Backend (FastAPI + MySQL)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then edit .env with your local MySQL password
```

Create the database (either let SQLAlchemy create tables automatically on
first run, or apply the schema directly):

```bash
mysql -u root -p < sql/schema.sql
```

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Visit `http://127.0.0.1:8000/docs` for interactive Swagger API docs.

Insert demo data (1 learner, 5 tutors):

```bash
python3 seed_data.py
```

### 2. Frontend (Flutter)

```bash
cd frontend
flutter pub get
```

Before running, set the correct backend URL in `lib/services/api_service.dart`:
- Android emulator → `http://10.0.2.2:8000` (already set as default)
- iOS simulator / desktop / web on the same machine → `http://127.0.0.1:8000`
- physical device → `http://<your-computer-LAN-IP>:8000`

```bash
flutter run
```

## Testing performed so far

- `backend/test_matching.py` — standalone unit tests for the compatibility
  scoring function (subject overlap, expertise scaling, preference
  matching, availability overlap, and descending-order ranking). Run with:
  ```bash
  cd backend && python3 test_matching.py
  ```
  All tests pass in this environment (pure Python, no external
  dependencies required).
- The FastAPI endpoints and the Flutter screens have been written and
  reviewed for correctness but **have not yet been run against a live
  MySQL instance or a Flutter emulator**, since those require tools not
  available in the environment this code was drafted in. Please run
  the steps above locally and report any errors — see "What remains"
  below.

## Review-2 completion status

| Feature | Status | Evidence |
|---|---|---|
| Flutter frontend | Completed (code) | 4 screens: Home, Learner Profile, Tutor Profile, Recommendations |
| Learner profile | Completed (code) | Form + `POST /api/learners` + `learners`/`learner_subjects`/`learner_availability` tables |
| Tutor profile | Completed (code) | Form + `POST /api/tutors` + `tutors`/`tutor_subjects`/`tutor_availability` tables |
| Subject/skills | Completed (code) | Shared `subjects` reference table, get-or-create helper |
| Learning preference | Completed (code) | Stored on learner/tutor, used in `preference_score()` |
| Availability | Completed (code) | Stored as slots, used in `availability_overlap_score()` |
| FastAPI | Completed (code) | `POST /api/learners`, `POST /api/tutors`, `GET /api/learners/{id}`, `GET /api/tutors`, `GET /api/matches/{learner_id}` |
| MySQL | Schema completed | `sql/schema.sql`; not yet run against a live server in this environment |
| Matching | Completed (code + tested) | `test_matching.py` passes; weighted compatibility score, not a trained model |
| Ranking | Completed (code + tested) | `rank_tutors()` sorts descending, verified in tests |
| Flutter–FastAPI connection | Implemented (code) | `ApiService` — not yet run end-to-end on a device/emulator |

**Local verification still required by the team:** running `uvicorn`
against a real MySQL database, running `flutter run` against a real
emulator/device, and confirming the full Flutter → FastAPI → MySQL →
matching → Flutter round trip end-to-end. Please run the steps above and
report back any errors so they can be fixed before the review.

## Limitations (Review-2)

- The matching algorithm is a simple, explainable weighted score — not a
  trained machine-learning model.
- No real user testing has been conducted yet.
- The backend/Flutter code has not yet been executed end-to-end against a
  live MySQL instance or emulator in this environment (see above).
- Sample data is for demonstration only (1 learner, 5 tutors) — not a
  research dataset.

## Future Work (Part 2 / Final Review)

- Advanced ML/recommendation techniques
- Session management
- Feedback collection and feedback-based recommendation improvement
- Additional personalization features
- User testing
- Performance evaluation
- Deployment and scalability
- Authentication and other security hardening
