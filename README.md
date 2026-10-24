# Task Management System

**CPSC 449 — Web Back-End Engineering | Semester Project**

A simple web-based task manager that helps users organize personal tasks, track deadlines, and monitor progress. This project focuses on core backend functionality rather than advanced productivity features or AI.

## Project Overview

Students and other busy users often struggle to keep track of tasks and due dates. Our application provides a straightforward dashboard where users can create, update, complete, and delete their tasks in one place.

**Category:** Productivity / Task Management  
**Status:** In development  
**Student 1:** Kamilo Ramirez  
**Student 2:** Dillon Noronha

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

## Planned Data Model

**Users**
- `id`
- `name`
- `email`
- `password_hash`
- `role` (`user` or `admin`)
- `created_at`

**Tasks**
- `id`
- `user_id` (references a user)
- `title`
- `description`
- `due_date`
- `status` (`todo`, `in_progress`, `completed`)
- `created_at`
- `updated_at`

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
| Implement authorization checks and admin API endpoints | Add `USER` and `ADMIN` roles with protected routes; build the admin interface |
| Integrate the public holiday API | Integrate Google Calendar and Resend APIs |
| Implement WebSocket server | Connect WebSocket updates to the UI |
| Build task analytics endpoint | Display task statistics |
| Deploy backend and database | Deploy frontend and connect production services |

**Both students:** Integration testing, debugging, code reviews, documentation, Git commits, and final presentation.

## Development Checklist

- [ ] Initialize repository and project structure
- [ ] Set up database and backend
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

## Getting Started

Local installation and run instructions will be added once the frontend, backend, and database project structures are finalized.

**Planned prerequisites:** Python, Node.js, PostgreSQL, and the necessary credentials for authenticated third-party services.

Secrets such as database passwords, JWT signing keys, OAuth client secrets, and Resend API keys must be stored in environment variables and **must not be committed to GitHub**.

## Project Scope

The initial version will **not** include AI-generated tips, shared team workspaces, chat, complex notifications, or drag-and-drop boards. The priority is meeting the course requirements with a small, functional application.

## Course

CPSC 449 — Web Back-End Engineering  
Semester Project — Kamilo Ramirez and Dillon Noronha
