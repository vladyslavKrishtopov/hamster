
 # Hamster
 
 A minimal Flask inventory prototype (development). This project stores users and inventory in SQLite using SQLAlchemy.
 
 ## Features
 - User registration and login (stored in SQLite)
 - Per-user inventory (each user sees only their items)
 - Item CRUD: create, edit, delete
 - Server-side SKU uniqueness enforced per user
 - Internal server-side item IDs (UUID) to avoid SKU collisions across users
 - Item fields: `sku`, `name`, `qty`, `location`, `category`, `description`, `purchase_price`
 - Smooth expand/collapse animation for item details in the UI
 
 ## Installation
 1. Create and activate a Python virtual environment (recommended):
 
 ```bash
 python3 -m venv .venv
 source .venv/bin/activate
 ```
 
 2. Install dependencies:
 
 ```bash
 python3 -m pip install -r requirements.txt
 ```
 
 3. Run the dev server (it will create `hamster.db` automatically):
 
 ```bash
 python3 app.py
 ```
 
 Open http://localhost:3000 in your browser.
 
 ## Project structure
 - `app.py` — Flask application entrypoint and routes (uses SQLAlchemy)
 - `models.py` — SQLAlchemy models: `User`, `Item` (unique constraint on `(owner_id, sku)`)
 - `templates/` — Jinja2 templates (login, register, table, form, dashboard)
 - `requirements.txt` — Python dependencies
 - `.gitignore` — ignored files (including `hamster.db`, `items.json`, `users.json`)
 - `hamster.db` — SQLite database (created at runtime)
 
 ## Data model (summary)
 - User: `id`, `username`, `email`, `password_hash`
 - Item: `id` (UUID), `sku`, `name`, `qty`, `location`, `category`, `description`, `purchase_price`, `owner_id`
 
 ## Security & production notes
 - `app.secret_key` is currently a development secret in `app.py`; set a secure value via environment variable for production.
 - SQLite is fine for local/small setups; for multi-process production use PostgreSQL or MySQL.
 - Consider integrating `Flask-Login` for robust session management and `Flask-Migrate` for migrations.
 
 ## Testing the app
 - Register a user at `/register`, sign in, then add items at `/items/new`.
 - The UI enforces SKU uniqueness per user and stores the purchase price as a float.
 
 If you'd like, I can add a small admin view, enable `Flask-Login`, or provide a one-off import script — tell me which next.

Important files & paths
-----------------------

- `app.py` — application entrypoint and routes (uses SQLAlchemy + SQLite).
- `models.py` — SQLAlchemy models for `User` and `Item`.
- `requirements.txt` — Python dependencies.
- `templates/` — HTML templates:
	- `main.html` — login page
	- `register.html` — user registration
	- `table.html` — main inventory table (home)
	- `form.html` — add / edit item form
	- `dashboard.html` — dashboard preview
	- `preview/*` routes available to preview templates without login
- `.gitignore` — ignored files (including `hamster.db`)
- `hamster.db` — SQLite database file created when the app runs

Routes (overview)
-----------------

- `/` — Login page (GET/POST).
- `/register` — Registration page (GET/POST).
- `/home` — Inventory table (requires login).
- `/logout` — Log out and return to login.
- `/items/new` — Create item (GET/POST).
- `/items/<item_id>/edit` — Edit item (GET/POST).
- `/items/<item_id>/delete` — Delete item (POST).
- `/preview/table`, `/preview/dashboard`, `/preview/form` — template previews.