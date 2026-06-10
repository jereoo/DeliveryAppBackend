# Observability — auth and registration (stub)

**Last updated:** June 9, 2026  
**Scope:** Phase 2 logging for login and registration failures on `DeliveryAppBackend`.

---

## Logger

| Logger name | Level | Purpose |
|-------------|-------|---------|
| `delivery.auth` | WARNING+ | Failed JWT login and registration validation |

Logs go to **stdout** (Heroku log drain). Passwords and registration field **values** are never logged.

---

## Events

### `auth.login_failed`

Emitted when `POST /api/token/` fails validation (bad username/password).

| Field | Description |
|-------|-------------|
| `event` | `auth.login_failed` |
| `username` | Submitted username (truncated to 150 chars) |
| `request_id` | Correlation id (`X-Request-ID` header or generated UUID) |
| `path` | Request path |
| `method` | HTTP method |
| `remote_addr` | Client IP when available |

### `registration.validation_failed`

Emitted when `POST /api/customers/register/` or `POST /api/drivers/register/` returns 400.

| Field | Description |
|-------|-------------|
| `event` | `registration.validation_failed` |
| `registration_type` | `customer` or `driver` |
| `fields` | Sorted list of invalid field names only |
| `request_id` | Same as above |
| `path` | Request path |
| `method` | HTTP method |
| `remote_addr` | Client IP when available |

---

## Request correlation

`delivery.middleware.RequestIdMiddleware` sets `request.request_id` and returns `X-Request-ID` on every response. Clients may send their own `X-Request-ID` header to tie mobile errors to server logs.

---

## Heroku

```bash
heroku logs --tail -a truck-buddy
```

Filter locally:

```bash
heroku logs -a truck-buddy -n 200 | findstr /i "JWT login Registration validation"
```

---

## Future (Phase 4+)

- Ship logs to a dedicated aggregator (Datadog, Papertrail, etc.)
- Metrics: login failure rate, registration failure by field
- Alerts on auth failure spikes
