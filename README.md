# Django Cookie-Based Authentication API

Authentication system built with Django + Django REST Framework, using an
**HttpOnly cookie** (`auth_token`) for login and **CSRF protection** on every request.
Registration is confirmed with a 6-digit OTP sent by email.

## Requirements

- Python 3.10 or newer
- Git

## Setup

**1. Clone the project**

```bash
git clone https://github.com/vinaydheeraj1234/django-auth-assignment.git
```

```bash
cd django-auth-assignment
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
```

Then activate it — on Windows:

```bash
venv\Scripts\activate
```

on macOS / Linux:

```bash
source venv/bin/activate
```

You should now see `(venv)` at the start of your terminal line.

**3. Install the dependencies**

```bash
pip install -r requirements.txt
```

**4. Create the `.env` file**

The project reads its settings from a `.env` file in the project root (next to `manage.py`).
This file is **not** in Git, so you have to create it yourself. Without it the server
starts but every request fails with `The SECRET_KEY setting must not be empty.`

First generate a secret key (Django has a helper for this, so run it after step 3):

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

That prints a random 50-character string, for example:

```
9cycieh+10@vpg6##!ckf$q_l1_d-9mecw-+e)hw696z_78p)y
```

Now create a file named `.env` in the project root and paste your key into it:

```
SECRET_KEY=paste-the-generated-key-here
```

**5. (Optional) Send real OTP emails**

If you skip this, the OTP is printed in the terminal where the server is running —
which is fine for testing. To send real email instead, add a Gmail address and a
[Gmail App Password](https://myaccount.google.com/apppasswords) (a normal Gmail
password will not work) to the same `.env` file:

```
SECRET_KEY=paste-the-generated-key-here
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-16-character-app-password
```

**6. Create the database tables**

```bash
python manage.py migrate
```

**7. Run the server**

```bash
python manage.py runserver
```

## Using it

| URL | What it is |
|---|---|
| http://127.0.0.1:8000/ | Small HTML page to test the whole flow |
| http://127.0.0.1:8000/swagger/ | Swagger API docs (also sets the `csrftoken` cookie) |
| http://127.0.0.1:8000/admin/ | Django admin |

### API endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/register/` | Takes `email` + `password`, emails a 6-digit OTP |
| POST | `/api/register/verify/` | Takes `email` + `otp`, activates the account |
| POST | `/api/login/` | Takes `email` + `password`, sets the `auth_token` cookie |
| GET | `/api/me/` | Returns the logged-in user (needs the cookie) |
| POST | `/api/logout/` | Deletes the token and clears the cookie |

### Typical flow

1. Open `/` or `/swagger/` once so the browser gets the `csrftoken` cookie.
2. `POST /api/register/` with your email and password.
3. Copy the OTP from the terminal (or your inbox) and `POST /api/register/verify/`.
4. `POST /api/login/` — the `auth_token` cookie is set automatically.
5. `GET /api/me/` — works because the browser sends the cookie on its own.
6. `POST /api/logout/` — after this, `/api/me/` returns 403 again.

> Every write request needs the `X-CSRFToken` header. Swagger and the HTML test page
> both add it for you automatically from the `csrftoken` cookie.

## Notes

- `auth_token` is **HttpOnly**, so JavaScript cannot read it. Authentication is
  cookie-only — sending the token in an `Authorization` header will not work.
- Logout deletes the token from the database, so an old copy of the cookie is useless.
- The OTP is valid for 10 minutes.
