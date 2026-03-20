# SmartMailboxApp: AI-Powered Email Intelligence System

SmartMailboxApp is a sophisticated email management platform that uses Generative AI (Google Gemini) and Rule-based NLP to categorize, summarize, and extract actionable tasks from your emails across multiple providers.

![App Screenshot](https://raw.githubusercontent.com/Spectronyx/SmartMailBoxApp/main/screenshots/dashboard_v1.png)

## 🌟 Key Features

### 📨 Smart Email Synchronization
- **Multi-Account Support**: Sync multiple mailboxes (Gmail, Outlook, Yahoo, and generic IMAP).
- **Gmail API Integration**: Secure OAuth2-based syncing for Gmail accounts.
- **Robust Header Decoding**: Handles RFC 2047 encoded headers (UTF-8, Base64, etc.) for perfect title and sender rendering.

### 🧠 AI Intelligence Layer
- **Auto-Classification**: Categorizes emails into CRITICAL, OPPORTUNITY, INFO, or JUNK using a hybrid Gemini AI + Rule-based pipeline.
- **Abstractive Summarization**: Generates concise, 3-4 sentence summaries of long emails using Gemini 2.0 Flash.
- **Task Extraction**: Automatically identifies "Action Items" and "Deadlines" from email content.
- **Privacy-First Cleaning**: Strips HTML, CSS, and scripts before processing to ensure AI models only see relevant text.

### 📋 Task Management
- **Automated To-Dos**: Extracted tasks are automatically added to your dashboard.
- **Deadline Tracking**: AI identifies dates like "tomorrow at 5 PM" or "next Friday" and maps them to actual timestamps.
- **Email Reminders**: (In development) Automated notifications for upcoming deadlines.

### 🎨 Modern Dashboard
- **Responsive UI**: Built with React, Tailwind CSS, and Vite.
- **Unified Inbox**: View all your emails from every account in one place.
- **Clean Rendering**: Sanitzed email body rendering with custom CSS to fix font contrast and layout issues.

## 🏗️ Project Architecture

The project consists of two main components:

- **[SmartMailboxBackend](./SmartMailboxBackend)**: Django REST Framework API with AI processing pipelines and IMAP/OAuth2 integration.
- **[SmartMailboxFrontend](./SmartMailboxFrontend)**: React single-page application for a seamless user experience.

## 🚀 Getting Started

### 1. Backend Setup (Django)
```bash
cd SmartMailboxBackend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
*Note: Requires a `.env` file with `GEMINI_API_KEY`.*

### 2. Frontend Setup (React)
```bash
cd SmartMailboxFrontend
npm install
npm run dev
```

## 🛠️ Tech Stack

- **Frontend**: React 19, Tailwind CSS 4, Vite, Lucide Icons, Axios.
- **Backend**: Django 6, Django REST Framework, Celery, Redis.
- **AI/NLP**: Google Gemini 2.0 Flash, Bleach (Sanitization), Dateparser.
- **Authentication**: JWT (SimpleJWT) & OAuth2 (Social Auth).

## 📄 License
This project was developed for the PEP Project.
