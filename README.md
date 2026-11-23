# Task Management System

**CPSC 449 — Web Back-End Engineering | Semester Project**

A simple web-based task manager that helps users organize personal tasks, track deadlines, and monitor progress. This project focuses on core backend functionality rather than advanced productivity features or AI.

## Project Overview

Students and other busy users often struggle to keep track of tasks and due dates. Our application provides a straightforward dashboard where users can create, update, complete, and delete their tasks in one place.

**Category:** Productivity / Task Management  
**Status:** In development  
**Student 1:** Kamilo Ramirez  
**Student 2:** Dillon Noronha

## Implemented backend foundation

The backend uses Python 3.11, FastAPI, PostgreSQL, SQLAlchemy, Pydantic, psycopg,
and Alembic. Apply the existing migrations before starting it.

| Method | Route | Access and success response |
| --- | --- | --- |
| GET | `/` | Public, 200 with application status |
| GET | `/health/db` | Public, 200 when PostgreSQL responds, 503 otherwise |
| POST | `/auth/login` | Public, 200 with an expiring JWT bearer token |
| GET | `/auth/me` | Signed in, 200 with `id`, `name`, `email`, and `role` |
| POST | `/tasks` | Signed-in owner, 201 with the created task |
| GET | `/tasks` | Signed-in owner, 200 with owned tasks ordered by ID |
| GET | `/tasks/{task_id}` | Signed-in owner, 200 with the requested task |
| PUT | `/tasks/{task_id}` | Signed-in owner, 200 with the updated task |
| DELETE | `/tasks/{task_id}` | Signed-in owner, 204 with an empty body |

Both roles use the same owner-scoped task routes. A task owned by someone else,
an unowned task, and a nonexistent task all return 404 on item routes. Existing
unowned rows stay in PostgreSQL and are excluded from task listings. The API
assigns new tasks to the authenticated user and rejects a request body containing
`user_id` with 422.

POST and PUT accept the same fields. Titles are trimmed and must contain 1–255
characters. Status is a trimmed string of 1–50 characters, defaulting to
`todo`. Description and due date are optional and default to null. PUT replaces
all writable fields while preserving the ID, owner, and creation timestamp. Send
all writable values you want to retain. Use a timezone offset in due dates.

## Planned Features

- **Registration:** Allow users to create accounts. Login is implemented.
- **Admin functionality:** Add protected administrative features using the backend role guard.
- **Basic analytics:** Display task totals and completion statistics.
- **Integrations:** Show public holidays, optionally add deadlines to Google Calendar, and send email reminders.

## Planned Technology Stack

| Component | Technology |
| --- | --- |
| Frontend | React |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Authentication | JWT |
| Real-time communication | WebSockets |
| Deployment | Railway (planned) |
| Version control | Git and GitHub |

## Planned API Integrations

| API | Access | Purpose |
| --- | --- | --- |
| [Nager.Date Holiday API](https://date.nager.at/Api) | Public | Display public holidays near task due dates. |
| [Google Calendar API](https://developers.google.com/workspace/calendar/api/guides/overview) | OAuth 2.0 | Allow users to add task deadlines to their calendar. |
| [Resend API](https://resend.com/docs/api-reference/introduction) | API key | Send task reminder emails. |

Our own FastAPI service will also expose authenticated endpoints for managing users and tasks.

## Planned Backend Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/auth/register` | Create an account. |
| GET | `/analytics` | Retrieve basic task statistics. |
| GET | `/admin/users` | List users using the admin guard. See the contract below. |

## Team Responsibilities

| Student 1 — Kamilo Ramirez (Core Backend) | Student 2 — Dillon Noronha (Frontend & Integrations) |
| --- | --- |
| Set up FastAPI and PostgreSQL | Set up React and frontend routing |
| Implement user authentication and JWT | Build login and registration pages |
| Implement task models and CRUD endpoints | Build task dashboard and forms |
| Implement internal API authorization later | Implement admin functionality and interface later |
| Configure database models and internal API endpoints | Integrate public holidays, Google Calendar, and Resend APIs |
| Implement WebSocket server | Connect WebSocket updates to the UI |
| Build task analytics endpoint | Display task statistics |
| Deploy backend and database | Deploy frontend and connect production services |

**Both students:** Integration testing, debugging, code reviews, documentation, Git commits, and final presentation.

## Development Checklist

- [x] Initialize repository and backend project structure
- [x] Set up database and backend
- [x] Add users/task relationship and Alembic migrations
- [x] Seed 3 fictional users and 12 repeatable development tasks
- [x] Build JWT login
- [ ] Build registration
- [x] Implement owner-scoped task CRUD
- [x] Provide a database-backed admin role guard
- [ ] Implement the protected admin endpoint and UI
- [ ] Build task dashboard
- [ ] Connect public holiday API
- [ ] Connect Google Calendar API
- [ ] Connect Resend API
- [x] Implement owner-scoped WebSocket task notifications
- [ ] Connect real-time task notifications to the client
- [ ] Add task analytics
- [ ] Test the application
- [ ] Deploy frontend, backend, and database
- [ ] Prepare project presentation and demonstration

## Getting Started — Windows PowerShell

Prerequisites for this checkpoint: Python 3.11 and a running PostgreSQL server.
Install PostgreSQL yourself if needed; no automatic system configuration is used.
The PostgreSQL commands below require its `bin` directory on PATH. Alternatively,
run the SQL in pgAdmin's Query Tool. Node.js and external API credentials are not
needed for this backend checkpoint.

On this machine PostgreSQL 18 is installed. To make its tools available in the
current PowerShell terminal (without changing system configuration):

```powershell
$env:Path = "C:\Program Files\PostgreSQL\18\bin;" + $env:Path
```

From the repository root:

```powershell
Set-Location .\backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Do not overwrite an existing `.env` containing your settings.

For a **new installation only**, create the database once using your PostgreSQL
administrator account. Skip this step for the existing `task_manager` database:

```powershell
psql -h localhost -p 5432 -U postgres -d postgres -W -c "CREATE DATABASE task_manager;"
```

Edit `backend/.env` locally and replace `CHANGE_ME` with your password:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:CHANGE_ME@localhost:5432/task_manager
```

URL-encode special characters in the username/password (for example, `@` becomes
`%40`). `.env` and virtual environments are ignored by Git. An existing
`DATABASE_URL` environment variable takes precedence over `.env`. The application
requires the `postgresql+psycopg` driver prefix and loads `.env` relative to the
backend directory, regardless of the shell's current directory.

### Apply migrations and seed development data

Stop your development server before upgrading. From `backend/`, with `.env` configured:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe scripts/seed.py
.\.venv\Scripts\python.exe scripts/seed.py
.\.venv\Scripts\python.exe -m alembic check
```

Revision `0001_task_baseline` recognizes and validates the original five-column
`tasks` table without rebuilding it, or creates that table on an empty database.
Revision `0002_users_and_task_details` creates users and adds nullable `user_id`,
`due_date`, and `seed_key` columns to tasks, plus a foreign key and unique seed
keys. Legacy tasks keep their original fields and get null new fields. PostgreSQL
runs these changes transactionally. No migration drops, truncates, or resets data.
Unexpected preexisting schemas fail for manual review. Offline migration output
and destructive downgrades are disabled; use reviewed forward migrations.
Do not use `alembic stamp head` to bypass schema changes.

The seed script creates Alex Morgan and Jordan Lee as users and Taylor Brooks as
an admin, all using fictional `example.com` addresses. Each owns four realistic
tasks spanning `todo`, `in_progress`, and `completed`. Due dates are fixed in
November 2026 at 17:00 UTC for reproducibility. All sample password hashes are
NULL. Use the dedicated local demo accounts below for authenticated testing.

Stable `cpsc449:v1:user:*` and `cpsc449:v1:task:*` keys identify sample records.
Reruns update their sample fields while keeping IDs/creation timestamps, never
matching tasks by title. Unrelated records remain untouched. A conflicting email
on an unrelated user, or login credentials on a sample user, causes the whole
transaction to roll back. Database uniqueness constraints and a transaction-scoped
PostgreSQL advisory lock protect against concurrent seed runs. No reset/delete
option is provided. Run this script only against a development database.

### Configure and start the demo

From `backend/`, set `JWT_SECRET` in the server environment or the ignored
`.env`. Generate a random value of at least 32 bytes. For example:

```powershell
$env:JWT_SECRET = .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set distinct `DEMO_USER_PASSWORD` and `DEMO_ADMIN_PASSWORD` values (12–1024
characters) in the local environment or ignored `.env`. With `DATABASE_URL`
pointing to a disposable local database and migrations applied:

```powershell
.\.venv\Scripts\python.exe scripts/provision_demo_accounts.py --confirm-local-demo
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --ws-max-size 4096
```

The provisioning command creates `demo.user@example.com` (`user`) and
`demo.admin@example.com` (`admin`). Reruns update credentials in place and
preserve IDs. A collision with an unrelated account rolls back the pair. The
original sample accounts keep their null password hashes.

API base URL is `http://127.0.0.1:8000`. Open Swagger at
`http://127.0.0.1:8000/docs`. Set `FRONTEND_ORIGINS` to the client origins
that should be allowed to call the API from another origin, for example
`http://localhost:5173,http://127.0.0.1:5173`. Include the scheme and port.
Restart the API after changing its configuration.

### Login and task requests

Send JSON to `POST /auth/login`:

```json
{"email":"demo.user@example.com","password":"<local demo password>"}
```

The 200 response has this shape:

```json
{"access_token":"<redacted>","token_type":"bearer","expires_in":3600}
```

Send `Authorization: Bearer <access_token>` on protected requests. Use
`GET /auth/me` to initialize the client with the current user's ID, name,
email, and role. Incorrect credentials and missing, invalid, or expired
tokens return 401. Invalid request bodies return 422. Login and bearer-token
verification return 503 if the signing key is unavailable. Login and
protected routes return 503 if their database operation fails.

Task responses contain `id`, `title`, `description`, `status`, `created_at`,
`user_id`, and `due_date`. List responses are arrays of the same objects.
A write body may contain `title` (required), `description`, `status`, and
`due_date` (for example, `2026-12-01T17:00:00Z`). There is no owner input.

1. `POST /tasks` with `{"title":"Checkpoint disposable task","description":"CRUD proof"}`.
   Expect 201 and save the returned ID as `taskId`.
2. `GET /tasks` and `GET /tasks/{{taskId}}`. Expect 200 and the same ID.
3. `PUT /tasks/{{taskId}}` with `{"title":"Checkpoint disposable task","status":"completed"}`.
   Expect 200 with the same ID, the new status, and a null description.
4. `DELETE /tasks/{{taskId}}`. Expect 204 with an empty body.
5. `GET /tasks/{{taskId}}` returns 404. `GET /tasks` returns 200 with the ID absent.

Keep tokens and passwords out of screenshots and shared Postman exports.

### Admin route contract for Dillon

In Dillon's `backend/app/admin.py`, import `AdminUser` and use it as a
typed dependency on the handler:

```python
from fastapi import APIRouter
from sqlalchemy import select

from app.auth import AdminUser
from app.database import DbSession
from app.models import User
from app.schemas import UserSummary

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserSummary])
def list_users(db: DbSession, admin: AdminUser):
    rows = db.execute(select(User.id, User.name, User.email, User.role).order_by(User.id))
    return rows.mappings().all()
```

In `backend/app/main.py`, add `from . import admin` and register the router
with `app.include_router(admin.router)` after app creation. The contract
for `GET /admin/users` is 401 without a valid bearer token, 403 for a signed-in
non-admin, and 200 with an array of user summaries for an admin. The guard
checks the stored `admin` role on every request. The example selects only
response fields. This branch supplies the guard, and Dillon owns the actual
admin route and client.

### Nager.Date handoff

The available Dillon commit, `8faae68`, has three provider modules:
`backend/app/routers/holidays.py`, `backend/app/services/holiday_service.py`,
and `backend/app/schemas/holiday.py`. Port the holiday models to a distinct
module such as `app/holiday_schemas.py` so the existing `app/schemas.py` remains
the import target for auth and task models. Update both holiday imports, add
`httpx` (Dillon's branch declares `0.28.1`), carry over the
`NAGER_DATE_BASE_URL` and `DEFAULT_COUNTRY_CODE` settings, and register
`holidays.router` in `app/main.py`. Dillon's settings module uses
`pydantic-settings` (declared as `2.6.1`) if ported as-is. No database changes
are needed for the holiday lookups.

Keep the Alembic migrations and existing users/tasks models as the integration
base. Dillon's scaffold uses startup `create_all()`, uppercase enum roles and
statuses, required task ownership, date-only due dates, and different password
and foreign-key constraints. Port the provider modules independently of that
scaffold. Calendar and Resend have no implementation in the available refs.

### Live task updates

Connect to `ws://127.0.0.1:8000/ws/tasks` locally or `wss://<backend-host>/ws/tasks`
over HTTPS. In the browser's open handler, send the raw access token as the first
text frame within five seconds. Keep it out of URLs and logs. On
`{"type":"ready"}`, load `GET /tasks`. On `{"type":"tasks.changed"}`, load
`GET /tasks` again and update the client state. Events carry no task data and
can be coalesced. Refresh after reconnecting to catch up with any missed writes.
On token expiry, sign in again and reconnect. Browser origins must match the
backend origin or be listed in `FRONTEND_ORIGINS`.

To demo, sign in as the same demo user in two sessions. Wait for both to load
their task list. Create, edit, or delete the demo task in session A and show the
change appearing in session B without manual refresh. A different account
receives no notification for those writes.

Task notifications are in memory. Run the demo with one backend instance and
one worker. Multiple instances or workers would need shared event delivery.
Only successful task writes through this API trigger notifications.

### Hosting and health

Railway is the planned host. Set the service root to `backend`, install
`requirements.txt`, set `DATABASE_URL` (with the `postgresql+psycopg` driver
prefix), `JWT_SECRET`, and the deployed `FRONTEND_ORIGINS`. Apply
`python -m alembic upgrade head` once per release before accepting traffic.
On a POSIX host that sets `PORT`, start with:

```sh
python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT" --workers 1 --ws-max-size 4096
```

Use `GET /` for process health and `GET /health/db` to verify connectivity.
`/health/db` returns `{"status":"ok","database":"connected"}` with 200 or a
503 on failure. It does not verify that migrations are current. This repository
does not yet supply a hosted URL. Provision demo accounts only for the isolated
demo environment.

### Verify seed counts and relationships

Run these queries in pgAdmin, or connect using
`psql -h localhost -p 5432 -U postgres -d task_manager -W`:

```sql
SELECT version_num FROM alembic_version;
SELECT id, name, email, role, password_hash IS NULL AS no_login, seed_key
FROM users ORDER BY id;
SELECT count(*) AS seeded_users FROM users
WHERE starts_with(seed_key, 'cpsc449:v1:user:'); -- 3
SELECT count(*) AS seeded_tasks FROM tasks
WHERE starts_with(seed_key, 'cpsc449:v1:task:'); -- 12
SELECT u.name, count(t.id) AS sample_tasks
FROM users u LEFT JOIN tasks t ON t.user_id = u.id
  AND starts_with(t.seed_key, 'cpsc449:v1:task:')
WHERE starts_with(u.seed_key, 'cpsc449:v1:user:')
GROUP BY u.id, u.name ORDER BY u.id; -- 4 each
SELECT t.id, t.title, t.status, t.due_date, u.name, t.seed_key
FROM tasks t LEFT JOIN users u ON u.id = t.user_id ORDER BY t.id;
SELECT count(*) AS orphaned_tasks FROM tasks t
LEFT JOIN users u ON u.id = t.user_id
WHERE t.user_id IS NOT NULL AND u.id IS NULL; -- 0
```

Secrets such as database passwords, JWT signing keys, OAuth client secrets, and Resend API keys must be stored in environment variables and **must not be committed to GitHub**.

## Project Scope

The initial version will **not** include AI-generated tips, shared team workspaces, chat, complex notifications, or drag-and-drop boards. The priority is meeting the course requirements with a small, functional application.

## Course

CPSC 449 — Web Back-End Engineering  
Semester Project — Kamilo Ramirez and Dillon Noronha
