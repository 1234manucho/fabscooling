# FABS Cooling Ltd — Flask Website

A production-ready Flask company website for cold rooms, insulated panels,
industrial refrigeration, HVAC, service and maintenance.

## Included

- Responsive, multi-page corporate website
- Original Arctic fox FABS Cooling logo mark with transparent PNG
- Tailwind CSS CDN plus custom inline CSS
- Mobile navigation and inline JavaScript interactions
- Working project enquiry form with reference numbers
- SQLite locally and PostgreSQL-ready configuration
- Protected enquiry-review dashboard
- Newsletter storage, CSRF protection, error pages and health endpoint

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask --app app init-db
flask --app app run
```

Open `http://127.0.0.1:5000`. The administrator login is at `/admin/login`.
Change `ADMIN_EMAIL`, `ADMIN_PASSWORD` and `SECRET_KEY` in `.env` before use.

## Deploy

The `Procfile` is ready for Render or another Gunicorn-compatible host. Set all
values from `.env.example` in the host's environment settings. For PostgreSQL,
set `DATABASE_URL` to the provider's connection string.
