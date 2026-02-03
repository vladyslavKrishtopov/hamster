
Hamster — Minimal Inventory Flask App
=====================================

Overview
--------

This is a small prototype web app for basic inventory management built with Flask. It is intended as a starting point — it uses JSON files for persistence so it's suitable for local development and demos only.

Key features
------------

- Login and registration (JSON-backed user store).
- Passwords hashed using Werkzeug utilities.
- Item store persisted to `items.json` with basic create / edit / delete functionality.
- Simple HTML templates (Bootstrap) for: login, registration, inventory table, add/edit form, dashboard preview.
- Preview routes to see alternate layouts without logging in.

Run (quick)
-----------

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app (development server on port 3000):

```bash
python app.py
```

4. Open your browser to `http://127.0.0.1:3000/` to see the login page. Use `Create one` to register a new user and then sign in.

Important files & paths
-----------------------

- `app.py` — application entrypoint, routes, and simple JSON-backed stores.
- `requirements.txt` — Python dependencies (`Flask`, `Werkzeug` is included with Flask).
- `templates/` — HTML templates:
	- `main.html` — login page
	- `register.html` — user registration
	- `table.html` — main inventory table (home)
	- `form.html` — add / edit item form
	- `dashboard.html` — dashboard preview
	- `preview/*` routes available to preview templates without login
- `users.json` — created when the first user registers (stores {username: {email, password_hash}})
- `items.json` — created when the first item is added (stores {sku: {name, qty, location, category, description}})

Routes (overview)
-----------------

- `/` — Login page (GET/POST).
- `/register` — Registration page (GET/POST).
- `/home` — Inventory table (requires login).
- `/logout` — Log out and return to login.
- `/items/new` — Create item (GET/POST).
- `/items/<sku>/edit` — Edit item (GET/POST).
- `/items/<sku>/delete` — Delete item (POST).
- `/preview/table`, `/preview/dashboard`, `/preview/form` — template previews.

Security & notes
----------------

- This prototype uses JSON files for storage and a development `SECRET_KEY` stored in source. For any real deployment:
	- Move `SECRET_KEY` to an environment variable.
	- Use a proper database (SQLite/Postgres) and migrations.
	- Add email verification, rate-limiting, and stronger password policies.

Feedback & next steps
--------------------

If you'd like, I can:

- Migrate users/items to SQLite + SQLAlchemy and integrate `Flask-Login`.
- Add a JSON REST API (`/api/items`) for programmatic access.
- Add Dockerfile and a simple deployment guide.

Enjoy — tell me what to implement next.

