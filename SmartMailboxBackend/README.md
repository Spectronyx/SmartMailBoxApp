# Smart Mailbox Summarizer Backend

A production-ready Django REST API backend for managing email mailboxes, emails, and tasks with ML/NLP integration capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
cd SmartMailboxBackend
source venv/bin/activate  # Already created
python manage.py runserver
```

### Test the API

```bash
python test_api.py
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000/api/
```

### Endpoints

#### Mailboxes
- `GET /api/mailboxes/` - List mailboxes
- `POST /api/mailboxes/` - Create mailbox
- `GET /api/mailboxes/{id}/` - Get mailbox details

#### Emails
- `GET /api/emails/` - Unified inbox
- `GET /api/emails/mailbox/{id}/` - Emails for specific mailbox
- `POST /api/emails/` - Create email
- `GET /api/emails/{id}/` - Email details

**Filters**: `?category=CRITICAL`, `?mailbox=1`

#### Tasks
- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `GET /api/tasks/{id}/` - Task details

**Filters**: `?reminder_sent=false`

## 🏗️ Project Structure

```
SmartMailboxBackend/
├── config/          # Django settings
├── mailboxes/       # Mailbox app
├── emails/          # Email app
├── tasks/           # Task app
├── accounts/        # User accounts (future)
└── test_api.py      # API tests
```

## 📊 Models

### Mailbox
- `provider`: Email provider (GMAIL, OUTLOOK, etc.)
- `email_address`: Email address (unique)
- `is_active`: Active status

### Email
- `subject`, `sender`, `body`: Email content
- `received_at`: Timestamp
- `category`: CRITICAL, OPPORTUNITY, INFO, JUNK (ML-ready)
- `summary`: AI-generated summary (nullable)
- `extracted_deadline`: NLP-extracted deadline (nullable)
- `mailbox`: Foreign key to Mailbox

### Task
- `action_text`: Task description
- `deadline`: Due date
- `reminder_sent`: Reminder status
- `email`: Foreign key to Email

## 🔧 Tech Stack

- **Framework**: Django 6.0.1
- **API**: Django REST Framework 3.16.1
- **Database**: SQLite (dev), PostgreSQL-ready
- **Filtering**: django-filter

## 🎯 Features

✅ Full CRUD operations for all models  
✅ Unified inbox across multiple mailboxes  
✅ Advanced filtering and search  
✅ Pagination (20 items/page)  
✅ ML-ready fields for future integration  
✅ Django Admin interface  
✅ Browsable API  

## 🔮 Future Enhancements

- **Sprint 2**: JWT authentication
- **Sprint 3**: ML/NLP integration (categorization, summarization)
- **Sprint 4**: Email fetching (IMAP, OAuth2)
- **Sprint 5**: Reminder notifications

## 📝 Admin Panel

Create a superuser:
```bash
python manage.py createsuperuser
```

Access at: `http://localhost:8000/admin/`

## 🧪 Testing

All endpoints tested and verified:
- Mailbox CRUD ✅
- Email operations ✅
- Task management ✅
- Filtering & search ✅

## 📄 License

This project is for the PEP Project.
