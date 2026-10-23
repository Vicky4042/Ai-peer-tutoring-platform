# Flutter frontend

## Start the app

Run the FastAPI backend first (see the root `README.md`), then:

```powershell
cd frontend
flutter pub get
flutter run -d chrome
```

The app calls `http://127.0.0.1:8000` by default. For an Android emulator, change `ApiService.baseUrl` to `http://10.0.2.2:8000`.

The app includes learner/tutor profile creation, AI recommendations, session requests, learning materials, progress logging, session management, and post-session feedback.
