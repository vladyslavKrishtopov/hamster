from flask import Flask, render_template, request, redirect, url_for, session, abort
import json
import uuid
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# WARNING: for production set a secure random secret key, e.g. from environment
app.secret_key = 'dev-secret'

# Simple JSON-backed user store (not for production). File path: users.json
USERS_PATH = Path(__file__).parent / 'users.json'


def load_users():
    if not USERS_PATH.exists():
        return {}
    try:
        with open(USERS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users: dict):
    with open(USERS_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)


# Simple JSON-backed items store (keyed by internal id)
ITEMS_PATH = Path(__file__).parent / 'items.json'


def load_items():
    if not ITEMS_PATH.exists():
        return {}
    try:
        with open(ITEMS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_items(items: dict):
    with open(ITEMS_PATH, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=2)

@app.route('/', methods=['GET', 'POST'])
def home():
    # Login page (main). POST to log in, GET to show form.
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        users = load_users()
        user = users.get(username)
        if user and check_password_hash(user.get('password_hash', ''), password):
            session['user'] = username
            return redirect(url_for('home_page'))
        else:
            return render_template('main.html', error='Invalid credentials')
    # GET
    # allow message via query string (e.g. after registration)
    message = request.args.get('message')
    return render_template('main.html', message=message)


@app.route('/home')
def home_page():
    # require login
    if 'user' not in session:
        return redirect(url_for('home'))
    user = session.get('user')
    items = load_items()
    # items stored as dict keyed by internal id -> item dict
    # show only items owned by the current user; include the internal id
    items_list = [dict(id=item_id, **data) for item_id, data in items.items() if data.get('owner') == user]
    return render_template('table.html', items=items_list)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if not username or not email or not password:
            return render_template('register.html', error='All fields are required')
        if password != confirm:
            return render_template('register.html', error='Passwords do not match')

        users = load_users()
        if username in users:
            return render_template('register.html', error='Username already exists')

        users[username] = {
            'email': email,
            'password_hash': generate_password_hash(password)
        }
        save_users(users)
        return redirect(url_for('home', message='Account created — please sign in'))

    return render_template('register.html')


@app.route('/preview/dashboard')
def preview_dashboard():
    return render_template('dashboard.html')


@app.route('/preview/table')
def preview_table():
    return render_template('table.html')


@app.route('/preview/form')
def preview_form():
    return render_template('form.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


@app.route('/items/new', methods=['GET', 'POST'])
def create_item():
    if 'user' not in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        sku = request.form.get('sku', '').strip()
        name = request.form.get('name', '').strip()
        qty = request.form.get('qty', '0')
        location = request.form.get('location', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        purchase_price_raw = request.form.get('purchase_price', '').strip()
        try:
            purchase_price = float(purchase_price_raw) if purchase_price_raw != '' else 0.0
        except ValueError:
            purchase_price = 0.0

        if not sku or not name:
            return render_template('form.html', error='SKU and name required', action=url_for('create_item'))

        items = load_items()
        # Always assign owner server-side from session
        owner = session.get('user')
        # Enforce SKU uniqueness per-user
        if any(d.get('sku') == sku and d.get('owner') == owner for d in items.values()):
            return render_template('form.html', error='SKU already exists for this user', action=url_for('create_item'))
        # Use an internal UUID as the items dict key
        item_id = str(uuid.uuid4())
        items[item_id] = {
            'sku': sku,
            'name': name,
            'qty': int(qty) if qty.isdigit() else 0,
            'location': location,
            'category': category,
            'description': description,
            'purchase_price': purchase_price,
            'owner': owner,
        }
        save_items(items)
        return redirect(url_for('home_page'))

    return render_template('form.html', action=url_for('create_item'))


@app.route('/items/<item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    if 'user' not in session:
        return redirect(url_for('home'))
    items = load_items()
    item = items.get(item_id)
    if not item:
        return redirect(url_for('home_page'))
    # only owner may edit
    if item.get('owner') != session.get('user'):
        abort(403)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        qty = request.form.get('qty', '0')
        location = request.form.get('location', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        purchase_price_raw = request.form.get('purchase_price', '').strip()
        try:
            purchase_price = float(purchase_price_raw) if purchase_price_raw != '' else item.get('purchase_price', 0.0)
        except ValueError:
            purchase_price = item.get('purchase_price', 0.0)

        if not name:
            return render_template('form.html', error='Name required', item=item, action=url_for('edit_item', item_id=item_id))

        item.update({
            'name': name,
            'qty': int(qty) if qty.isdigit() else 0,
            'location': location,
            'category': category,
            'description': description,
            'purchase_price': purchase_price,
        })
        items[item_id] = item
        save_items(items)
        return redirect(url_for('home_page'))

    # GET
    # provide item and action (include id for templates)
    data = dict(item)
    data['id'] = item_id
    data['sku'] = item.get('sku')
    return render_template('form.html', item=data, action=url_for('edit_item', item_id=item_id))


@app.route('/items/<item_id>/delete', methods=['POST'])
def delete_item(item_id):
    if 'user' not in session:
        return redirect(url_for('home'))
    items = load_items()
    if item_id in items:
        # enforce ownership before deleting
        if items[item_id].get('owner') != session.get('user'):
            abort(403)
        items.pop(item_id)
        save_items(items)
    return redirect(url_for('home_page'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
