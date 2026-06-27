# My Life in Words

A personal blog and journaling platform built with Django — a space for stories, reflections, and life lessons, with accounts so readers can sign up and join the conversation.

## Features

- **Custom accounts app** — email-based authentication (`CustomUser` with `email` as the `USERNAME_FIELD`), case-insensitive uniqueness on email/username.
- **Token-based registration flow** — request → email verification → account creation, backed by an expiring `RegistrationToken` (7-day default) with rotation for unverified/expired requests.
- **Transactional email** — verification and first-login emails sent via an on-commit hook (`utils/emailing`) so they only fire after the DB transaction succeeds; console backend in development, SMTP-configurable in production.
- **Profiles** — bio, avatar (private storage with `easy-thumbnails`), contact/data-sharing preferences, and linked websites.
- **Landing page** — `core` app serves the public home page.
- **Production-ready settings** — environment-driven config via `python-decouple`, Postgres/S3 support (`dj-database-url`, `django-storages`, `boto3`), static file serving via `whitenoise`, SQLite fallback for local development.

## Tech Stack

- Python 3.12+, Django 6.0
- PostgreSQL (production) / SQLite (development)
- `django-storages` + `boto3` for object storage, `easy-thumbnails` for image thumbnails
- `gunicorn` + `whitenoise` for serving
- Dev tooling: `ruff`, `black`, `pytest` / `pytest-django`, `django-debug-toolbar`

## Project Structure

```
accounts/   Custom user model, registration flow, profiles
core/       Public-facing pages (landing page)
config/     Django project settings, URLs, WSGI/ASGI
utils/      Shared helpers: emailing, storage, validators, admin actions
```

## Getting Started

1. **Install dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

2. **Configure environment variables**

   Create a `.env` file in the project root. At minimum:

   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   ```

   Generate a secret key with:

   ```bash
   make secret_key
   ```

   Other supported variables include `ALLOWED_HOSTS`, `DATABASE_URL`, `CSRF_TRUSTED_ORIGINS`, `EMAIL_*`, `DEFAULT_FROM_EMAIL`, `SUPPORT_EMAIL`, and `DJANGO_DEBUG_TOOLBAR` — see `config/settings.py` for the full list and defaults.

3. **Run migrations**

   ```bash
   python manage.py migrate
   ```

4. **Start the development server**

   ```bash
   make server
   ```

   The app will be available at `http://127.0.0.1:8000/`.

## Useful Commands

```bash
make secret_key   # Generate a new Django secret key
make shell        # Open a Django shell
make server       # Run the development server
pytest            # Run the test suite
ruff check .      # Lint
```
