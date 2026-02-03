from flask import Flask, render_template, request, redirect, url_for, session
import json
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


# Simple JSON-backed items store (keyed by SKU)
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
    items = load_items()
    # items stored as dict keyed by sku -> item dict
    # convert to list of tuples for predictable ordering
    items_list = [dict(sku=sku, **data) for sku, data in items.items()]
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

        if not sku or not name:
            return render_template('form.html', error='SKU and name required', action=url_for('create_item'))

        items = load_items()
        if sku in items:
            return render_template('form.html', error='SKU already exists', action=url_for('create_item'))

        items[sku] = {
            'name': name,
            'qty': int(qty) if qty.isdigit() else 0,
            'location': location,
            'category': category,
            'description': description,
        }
        save_items(items)
        return redirect(url_for('home_page'))

    return render_template('form.html', action=url_for('create_item'))


@app.route('/items/<sku>/edit', methods=['GET', 'POST'])
def edit_item(sku):
    if 'user' not in session:
        return redirect(url_for('home'))
    items = load_items()
    item = items.get(sku)
    if not item:
        return redirect(url_for('home_page'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        qty = request.form.get('qty', '0')
        location = request.form.get('location', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            return render_template('form.html', error='Name required', item=item, action=url_for('edit_item', sku=sku))

        item.update({
            'name': name,
            'qty': int(qty) if qty.isdigit() else 0,
            'location': location,
            'category': category,
            'description': description,
        })
        items[sku] = item
        save_items(items)
        return redirect(url_for('home_page'))

    # GET
    # provide item and action
    data = dict(item)
    data['sku'] = sku
    return render_template('form.html', item=data, action=url_for('edit_item', sku=sku))


@app.route('/items/<sku>/delete', methods=['POST'])
def delete_item(sku):
    if 'user' not in session:
        return redirect(url_for('home'))
    items = load_items()
    if sku in items:
        items.pop(sku)
        save_items(items)
    return redirect(url_for('home_page'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
