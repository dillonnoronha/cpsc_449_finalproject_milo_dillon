# Backend (FastAPI + PostgreSQL)

## Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app, registers routers
│   ├── core/config.py           # settings from environment / .env
│   ├── core/security.py         # password hashing (JWT goes here next)
│   ├── db/database.py           # SQLAlchemy engine, session, get_db dependency
│   ├── models/                  # users and tasks tables
│   ├── schemas/                 # Pydantic request/response models
│   ├── services/holiday_service.py  # Nager.Date public API client
│   └── routers/                 # health.py, holidays.py
├── scripts/seed.py              # resets and seeds sample data
├── requirements.txt
└── .env.example
```

## Run locally

1. Start PostgreSQL, either with Docker from the repo root (`docker compose up -d`)
   or a local PostgreSQL install with a database named `taskmanager`.
2. From the `backend` folder:

   ```bash
   python -m venv venv
   venv\Scripts\activate            # Windows  (macOS/Linux: source venv/bin/activate)
   pip install -r requirements.txt
   copy .env.example .env           # Windows  (macOS/Linux: cp .env.example .env)
   python -m scripts.seed           # creates tables + sample users/tasks
   uvicorn app.main:app --reload
   ```

3. Open http://127.0.0.1:8000/docs for interactive API docs.

## Endpoints so far

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | API status, database connection, and row counts |
| `GET` | `/holidays/{year}?country=US` | Public holidays for a year (Nager.Date) |
| `GET` | `/holidays/check?date=YYYY-MM-DD&country=US&window_days=3` | Whether a due date is on or near a public holiday |

## Seeded accounts

| Email | Password | Role |
| --- | --- | --- |
| admin@example.com | Admin123! | ADMIN |
| kamilo@example.com | Password123! | USER |
| dillon@example.com | Password123! | USER |

These are development-only sample accounts.
