# Admin bootstrap and password rotation

**Changing `ADMIN_PASSWORD` in the Heroku Dashboard (or with `heroku config:set`) does *not* update the Django user by itself.** Config vars are only loaded when a dyno runs. You must run `ensure_admin` after every password change so Django writes the new hash to Postgres:

```powershell
heroku run python manage.py ensure_admin -a truck-buddy
```

If the **old** password still works after that, Heroku is usually still running an older release that ignores `ADMIN_PASSWORD` — deploy current `main` from this repo (`git push heroku main`), then run the command above again.

Production must **not** use default passwords. The `ensure_admin` command reads credentials from environment variables only.

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ADMIN_PASSWORD` | Yes | — | Strong password (min 12 characters) |
| `ADMIN_USERNAME` | No | `admin` | Django superuser username |
| `ADMIN_EMAIL` | No | `admin@example.com` | Account email |

Copy `.env.example` to `.env` for local use. Never commit `.env` or real passwords.

## First-time production setup (Heroku)

```bash
# 1. Generate a strong password (save in your password manager)
# 2. Set config on the app (app name: truck-buddy)
heroku config:set ADMIN_PASSWORD="YOUR_STRONG_PASSWORD_HERE" -a truck-buddy
heroku config:set ADMIN_USERNAME=admin -a truck-buddy
heroku config:set ADMIN_EMAIL=you@yourdomain.com -a truck-buddy

# 3. Apply password to the database user
heroku run python manage.py ensure_admin -a truck-buddy
```

Log in via the mobile/web app or API:

```http
POST https://truck-buddy-f14f250ae8b3.herokuapp.com/api/token/
Content-Type: application/json

{"username":"admin","password":"<ADMIN_PASSWORD>"}
```

## Rotating the admin password

1. Choose a new password (12+ characters).
2. `heroku config:set ADMIN_PASSWORD="NEW_PASSWORD" -a truck-buddy`
3. `heroku run python manage.py ensure_admin -a truck-buddy`
4. Update your password manager; revoke old sessions if needed (JWTs expire per `SIMPLE_JWT` settings).

## Local development

```bash
# .env
ADMIN_USERNAME=admin
ADMIN_PASSWORD=local-dev-only-change-me
ADMIN_EMAIL=admin@localhost

python manage.py ensure_admin
```

## Security notes

- The old default `admin123` is **removed** from code. If production still accepts `admin123`, run `ensure_admin` with a new `ADMIN_PASSWORD` immediately.
- Do not put `ADMIN_PASSWORD` in `vercel.json`, mobile app config, or Git.
- Heroku config vars are the source of truth for production.
