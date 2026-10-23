# AI Peer Tutoring Platform

Flutter frontend and FastAPI backend for matching learners with peer tutors, discovering learning resources, requesting tutoring sessions, and tracking progress.

## Features

- Learner and tutor profiles with subject and availability information.
- AI-based tutor recommendations with compatibility scores and an explicit fallback scorer.
- Searchable, subject-filtered learning materials.
- Session requests, tutor acceptance/rejection, completion, and cancellation.
- Learner progress entries, session summaries, and post-completion feedback.
- REST API documentation through FastAPI Swagger UI.

## Requirements

- Python 3.10 or newer (Python 3.12 recommended).
- Flutter SDK and Chrome for the web frontend.
- Optional: MySQL. The default local setup uses SQLite and does not require a database server.

## Run the backend (PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
# Optional: copy .env.example to .env and configure DATABASE_URL.
python -m uvicorn app.main:app --reload --port 8000
```

The default database is `sqlite:///./peer_tutoring.db`, created in the `backend` folder. To use MySQL, set `DATABASE_URL` in `backend/.env` to a valid `mysql+pymysql://...` connection string.

API documentation: http://127.0.0.1:8000/docs
Health check: http://127.0.0.1:8000/health

## Seed learning materials

In a second terminal, from the `backend` directory with the virtual environment activated:

```powershell
python seed_resources.py
```

The seed is idempotent: running it repeatedly does not add duplicate URLs.

## Run the Flutter frontend

In a second terminal:

```powershell
cd frontend
flutter pub get
flutter run -d chrome
```

The web frontend defaults to `http://127.0.0.1:8000`. To override the backend URL without editing source, pass a Dart define:

```powershell
# Android emulator
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000

# Chrome (default can also be overridden)
flutter run -d chrome --dart-define=API_BASE_URL=http://127.0.0.1:8000
```

## Tests

Backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

Frontend:

```powershell
cd frontend
flutter analyze
flutter test
```

## Main API routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | Backend and ML availability |
| POST / GET | `/api/learners` | Create learner / retrieve learner by ID |
| POST / GET | `/api/tutors` | Create or list tutors |
| GET | `/api/matches/{learner_id}` | Ranked tutor recommendations |
| GET / POST | `/api/resources` | Search resources / add a resource |
| GET / POST | `/api/sessions` | List / request sessions |
| PATCH | `/api/sessions/{session_id}` | Accept, reject, complete or cancel a session |
| POST | `/api/sessions/{session_id}/feedback` | Submit feedback after completion |
| GET / POST | `/api/progress/{learner_id}` and `/api/progress` | Read / add learner progress |
| GET | `/api/progress/{learner_id}/summary` | Progress summary |

## Demo flow

1. Start the backend and seed learning materials.
2. Open the Flutter app in Chrome.
3. Create a tutor profile and retain the tutor ID.
4. Create a learner profile with at least one subject the tutor teaches.
5. Open the recommendations and request a session with a future date/time.
6. Open Manage Sessions, select Tutor, enter the tutor ID, and accept/reject the request.
7. Mark an accepted session completed.
8. Return to learner session management to submit feedback.
9. Use the progress screen from recommendations to log a topic and view the summary.

## Important notes

- The current prototype does not include authentication/authorization. Session role selection is for demonstration and is not secure for production use.
- The ML model was trained using synthetic labels. Its output is not a validated prediction of real-world tutoring success.
- Resource URLs are external learning resources; availability depends on the resource provider.
- Database schema changes are created for fresh/local development databases. Existing production databases should use a migration strategy before deploying.
