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

The backend uses Python 3.11, FastAPI, PostgreSQL, SQLAlchemy 2.x, Pydantic v2,
psycopg 3, and Alembic migrations. The following routes are implemented and were
verified against the local PostgreSQL 18 `task_manager` database.

| Method | Route | Behavior |
| --- | --- | --- |
| GET | `/` | Application status; does not check the database. |
| GET | `/health/db` | Executes `SELECT 1`; returns 503 if the database is unavailable. |
| POST | `/tasks` | Saves a task and returns HTTP 201 with its generated ID and timestamp. |
| GET | `/tasks` | Lists saved tasks by ID; returns `[]` when empty. |

Tasks currently contain `id`, `title`, optional `description`, `status` (default
`todo`), and a database-generated, timezone-aware `created_at`. Titles are trimmed
and must contain 1–255 characters. Status is a nonempty string up to 50 characters;
a fixed status enumeration is deferred. Tasks also have nullable `user_id` (foreign
key to `users.id`) and timezone-aware `due_date`. Both fields are optional in POST
and included in responses. Old requests and ownerless tasks remain valid. An
unknown owner ID returns HTTP 422. There is no authentication or access control;
GET still lists all tasks and specifying an owner does not authorize a request.
Update/delete operations remain planned.

Users contain `id`, required `name`, unique required `email`, nullable
`password_hash`, `role` (default `user`), and database-generated `created_at`.
`User.tasks` and `Task.user` form the one-to-many relationship. Both tables have
an internal nullable, unique `seed_key`, which is not exposed through the API.
Unseeded records leave this key null. No user, login, registration, or admin
endpoints have been added.

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py       # Routes; schema changes are handled by Alembic
│   ├── database.py   # Environment loading, engine, session dependency, Base
│   ├── models.py     # User/Task database models and relationship
│   └── schemas.py    # Request validation and ORM-compatible responses
├── migrations/       # Baseline and additive users/task migration
├── scripts/seed.py   # Transactional, repeatable synthetic development data
├── alembic.ini
├── requirements.txt
└── .env.example
```

Alembic now owns schema creation and upgrades; application startup no longer calls
`create_all()`. Sessions close after each request. Failed task writes roll back;
constraint errors return 422 and database availability errors return a generic 503
without connection details.

## Planned Features

- **User authentication:** Register and log in securely.
- **Task CRUD:** Create, view, edit, and delete personal tasks.
- **Task tracking:** Assign due dates and update task statuses (To Do, In Progress, Completed).
- **Real-time updates:** Reflect task changes across active sessions without a manual refresh.
- **Role-based access control:** Regular users manage their own tasks; admins access protected administrative features.
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

## Future Data Model Additions

The users/tasks foundation above is implemented. Future work includes authentication,
user ownership enforcement, role authorization, and a task `updated_at` field.

## Planned Backend Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | Create an account. |
| `POST` | `/auth/login` | Authenticate and receive a JWT. |
| `GET` | `/tasks` | Retrieve the logged-in user's tasks. |
| `POST` | `/tasks` | Create a task. |
| `PUT` | `/tasks/{id}` | Update an owned task. |
| `DELETE` | `/tasks/{id}` | Delete an owned task. |
| `GET` | `/analytics` | Retrieve basic task statistics. |
| `GET` | `/admin/users` | List users (admin only). |

Endpoint paths may change as development progresses.

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
- [ ] Build registration and login
- [ ] Implement task CRUD
- [ ] Add user/admin authorization
- [ ] Build task dashboard
- [ ] Connect public holiday API
- [ ] Connect Google Calendar API
- [ ] Connect Resend API
- [ ] Implement real-time task updates
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
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

If activation is blocked by PowerShell policy, use
`.\.venv\Scripts\python.exe` in place of `python`; activation is optional.
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
NULL, so they have no login credentials. An admin role value alone grants no
capability; there are no admin endpoints.

Stable `cpsc449:v1:user:*` and `cpsc449:v1:task:*` keys identify sample records.
Reruns update their sample fields while keeping IDs/creation timestamps, never
matching tasks by title. Unrelated records remain untouched. A conflicting email
on an unrelated user, or login credentials on a sample user, causes the whole
transaction to roll back. Database uniqueness constraints and a transaction-scoped
PostgreSQL advisory lock protect against concurrent seed runs. No reset/delete
option is provided. Run this script only against a development database.

Start from `backend/`:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open Swagger UI at **http://127.0.0.1:8000/docs**.
`/health/db` tests connectivity, not migration status or table existence. If task
queries fail after an update, confirm `alembic current` reports the head revision.
Apply migrations before starting the updated application.

### Checkpoint verification

In a second PowerShell terminal:

```powershell
curl.exe -i http://127.0.0.1:8000/
curl.exe -i http://127.0.0.1:8000/health/db
curl.exe -i http://127.0.0.1:8000/tasks

$task = Invoke-WebRequest -UseBasicParsing `
  -Method Post -Uri "http://127.0.0.1:8000/tasks" `
  -ContentType "application/json" `
  -Body '{"title":"Checkpoint database proof","description":"Created through FastAPI"}'
$task.StatusCode  # Expected: 201
$task.Content

curl.exe -i http://127.0.0.1:8000/tasks
psql -h localhost -p 5432 -U postgres -d task_manager -W -c "SELECT id, title, status, created_at FROM tasks ORDER BY id;"
```

On a new database, the first GET returns `[]`. After POST, GET and SQL should show
the same ID/title. Stop Uvicorn with Ctrl+C, restart it with the startup command,
and repeat GET `/tasks` to demonstrate persistence. Whitespace-only titles should
return HTTP 422 through Swagger UI. With PostgreSQL stopped, `/health/db` should
return HTTP 503 without credentials; restore PostgreSQL afterward.

Capture the backend directory tree, successful database health response, Swagger
POST with HTTP 201, and GET after restart alongside the matching SQL row. Hide
passwords and credential-bearing URLs. Describe these as successful only after
running them against PostgreSQL; imports or mocked tests do not prove persistence.

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

For a task with an owner, take an actual user ID from the query above and send
`{"title":"Review schema","user_id":1,"due_date":"2026-11-15T17:00:00Z"}`
through Swagger, replacing `1` if needed. Omitting both new fields still works.

### Verification performed during database expansion

- Inspected Git branch `main`, working tree, original models/configuration, and live
  database schema before edits. The existing `tasks` table contained **zero rows**.
- Applied both Alembic revisions against PostgreSQL 18; revision is
  `0002_users_and_task_details`. `alembic check` found no model/schema differences.
- Confirmed 3 sample users, NULL password hashes, 12 seeded tasks, four tasks per
  user, non-null due dates, and the database foreign key.
- Ran seed twice. Counts, IDs, ownership, due dates, and creation timestamps were
  unchanged; no duplicate samples appeared.
- Actual HTTP requests passed for GET `/`, GET `/health/db`, GET `/tasks`, and
  POST `/tasks` using the original request shape (201 with null new fields).
  A nonexistent user ID returned 422 without inserting a task.
- The second seed run preserved an unrelated API-created task unchanged. Final
  database has **12 seeded tasks plus 1 unseeded verification task** titled
  `Legacy request compatibility verification`. It was intentionally retained;
  no records were deleted. Since the original table was empty, preservation of
  nonempty pre-migration data was not exercised.
- `pip check` passed. Alembic was added to the local virtual environment. Credentials
  remained in ignored local configuration and were not printed or changed.

Recommended evidence: pgAdmin table columns/foreign key; the user list showing
`no_login`; seeded counts before/after rerun; joined task/owner rows; Swagger
GET `/health/db`, POST `/tasks` (201), and GET `/tasks`. Hide connection secrets.

Secrets such as database passwords, JWT signing keys, OAuth client secrets, and Resend API keys must be stored in environment variables and **must not be committed to GitHub**.

## Project Scope

The initial version will **not** include AI-generated tips, shared team workspaces, chat, complex notifications, or drag-and-drop boards. The priority is meeting the course requirements with a small, functional application.

## Course

CPSC 449 — Web Back-End Engineering  
Semester Project — Kamilo Ramirez and Dillon Noronha
