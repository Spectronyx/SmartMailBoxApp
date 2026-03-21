# Deployment Guide: SmartMailboxApp

This guide covers how to deploy the **SmartMailboxApp** (Backend and Frontend) to **Render** (or similar platforms like Vercel) without using Docker or custom start scripts.

---

## 🏗️ Backend Deployment (Django)

Deploy the backend as a **Render Web Service**.

### 1. Connection Details
*   **Repo Root**: `SmartMailboxBackend`
*   **Runtime**: `Python 3.14+`
*   **Build Command**:
    ```bash
    pip install -r requirements.txt && python manage.py migrate --noinput && python manage.py collectstatic --noinput
    ```
*   **Start Command**:
    ```bash
    gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
    ```

### 2. Required Environment Variables
Add these in the **Environment** tab of your Render service:
*   `DATABASE_URL`: Your Render PostgreSQL connection string.
*   `REDIS_URL`: Your Render Redis connection string.
*   `DEBUG`: `False` (Recommended for production)
*   `SECRET_KEY`: A long, random string.
*   `ALLOWED_HOSTS`: `localhost,127.0.0.1,your-app-name.onrender.com`
*   `GEMINI_API_KEY`: Your Google Gemini API Key.
*   `GOOGLE_OAUTH_CLIENT_ID`: Your Google OAuth Client ID.
*   `GOOGLE_OAUTH_CLIENT_SECRET`: Your Google OAuth Client Secret.
*   `GOOGLE_OAUTH_REDIRECT_URI`: `https://your-frontend-url.com/auth/google/callback`

---

## 📬 Frontend Deployment (React/Vite)

Deploy the frontend as a **Render Static Site** (Recommended) or Vercel.

### 1. Static Site Settings
*   **Repo Root**: `SmartMailboxFrontend`
*   **Build Command**: `npm install && npm run build`
*   **Publish Directory**: `dist`

### 2. Required Environment Variables
*   `VITE_API_BASE_URL`: `https://your-backend-name.onrender.com/api`

---

## ⚙️ Background Workers (Celery)

For full functionality (Email Syncing & AI Tasks), you need two additional **Render Web Services** (using the same codebase and environment variables as the main backend):

### 1. Celery Worker (Fetching & Processing)
*   **Start Command**: `celery -A config worker -l info`

### 2. Celery Beat (Scheduled Tasks)
*   **Start Command**: `celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

---

## 🛠️ Post-Deployment Checklist
1.  **Migrations**: Ensure the `migrate` command in the Build Command finished successfully (check logs for "Applying auth.0001_initial...").
2.  **HTTPS**: Render handles SSL automatically. Ensure your `ALLOWED_HOSTS` and OAuth redirect URIs use `https://`.
3.  **Database**: If you see `ProgrammingError: relation "auth_user" does not exist`, it means the migration in the Build Command failed. Check the logs for dependency issues.
