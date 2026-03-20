# SmartMailboxApp: AI-Powered Email Intelligence System

SmartMailboxApp is a sophisticated email management platform that uses Generative AI (Google Gemini) and Rule-based NLP to categorize, summarize, and extract actionable tasks from your emails across multiple providers.

![App Screenshot](https://raw.githubusercontent.com/Spectronyx/SmartMailBoxApp/main/screenshots/dashboard_v1.png)

## 🌟 Key Features

### 📨 Smart Email Synchronization
- **Multi-Account Support**: Sync multiple mailboxes (Gmail, IMAP).
- **Gmail API Integration**: Secure OAuth2-based syncing.
- **Automated Fetching**: Periodic background sync via Celery Beat.

### 🧠 AI Intelligence Layer
- **Auto-Classification**: CRITICAL, OPPORTUNITY, INFO, or JUNK categorization.
- **Abstractive Summarization**: Concise summaries using Gemini 2.0 Flash.
- **Task Extraction**: Automatically identifies "Action Items" and "Deadlines".

### 📋 Task & Calendar Management
- **Dashboard Tracking**: View all extracted tasks in a unified view.
- **Interactive Calendar**: Full-grid calendar view for deadline management.
- **Universal Export**: Download tasks as `.ics` files or add them to Google Calendar with one click.

### 🎨 Premium Aesthetics
- **Global Dark Mode**: Sleek, high-contrast dark theme with system sync.
- **Micro-Animations**: Fluid transitions and feedback powered by Framer Motion.
- **Advanced Search**: Powerful full-text search and granular filters (date ranges, attachments).

## 🏗️ Project Architecture

- **[SmartMailboxBackend](./SmartMailboxBackend)**: Django REST Framework + Celery + Gemini AI.
- **[SmartMailboxFrontend](./SmartMailboxFrontend)**: React + Tailwind CSS + Framer Motion.

## 🚀 Getting Started

### 1. Backend Setup
```bash
cd SmartMailboxBackend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
*Run `celery -A config worker -B` for periodic syncing.*

### 2. Frontend Setup
```bash
cd SmartMailboxFrontend
npm install
npm run dev
```

## 🛠️ Tech Stack

- **Frontend**: React 19, Tailwind CSS 4, Framer Motion, Lucide Icons, Date-fns.
- **Backend**: Django 6, DRF, Celery, Redis, Icalendar, Google GenAI.
- **AI**: Gemini 2.0 Flash.

## 📄 License
PEP Project.
