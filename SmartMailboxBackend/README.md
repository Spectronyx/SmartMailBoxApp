# Smart Mailbox Backend

A Django REST API powering the Smart Mailbox ecosystem with AI-driven categorization and task management.

## 🚀 API Features

- **Advanced Filtering**: Filter emails by `sender`, `category`, `mailbox`, `received_at` (range), and `has_attachments`.
- **Full-Text Search**: Search across `subject`, `sender`, `body`, and `summary`.
- **Calendar Integration**: Export tasks to standard `.ics` format.
- **AI Processing**: Dedicated endpoints for classification, summarization, and task extraction.
- **Periodic Sync**: Automated mailbox fetching using Celery Beat.

## 🛠️ Endpoints

### Emails
- `GET /api/emails/` - Supports `?search=`, `?category=`, `?received_at_after=`, etc.
- `POST /api/emails/classify/` - Trigger batch classification.
- `POST /api/emails/summarize/` - Trigger batch summarization.
- `POST /api/emails/extract-tasks/` - Trigger task extraction.

### Tasks
- `GET /api/tasks/` - List all extracted tasks.
- `GET /api/tasks/{id}/export-ics/` - Download a single task .ics.
- `GET /api/tasks/export-calendar/` - Download all tasks as a calendar.
- `POST /api/tasks/run-reminders/` - Manual reminder check.

## 🚀 Deployment

For production setup on platforms like **Render** or **Vercel**, refer to the unified [DEPLOYMENT.md](../DEPLOYMENT.md) in the project root.

---

## 🛠️ Setup & Development (Local)

```bash
# Activation
source venv/bin/activate

# Server
python manage.py runserver

# Background Workers (Required for Sync/AI)
celery -A config worker -l info
celery -A config beat -l info
```

## 📚 Tech Details
- **Django Filters**: Custom `EmailFilter` for complex date/relational queries.
- **Icalendar**: RFC 5545 compliant calendar generation.
- **Gemini SDK**: Version 0.7.2+ for Flash processing.
