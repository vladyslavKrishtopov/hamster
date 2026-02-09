from flask import Flask, render_template, request, redirect, url_for, session, abort
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Item
from flask_migrate import Migrate


app = Flask(__name__)
# WARNING: for production set a secure random secret key, e.g. from environment
app.secret_key = 'dev-secret'

# SQLAlchemy / SQLite config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hamster.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# initialize DB
db.init_app(app)
migrate = Migrate(app, db)


@app.route('/', methods=['GET', 'POST'])
def home():
    # Login page (main). POST to log in, GET to show form.
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user'] = username
            session['user_id'] = user.id
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
    user_id = session.get('user_id')
    # query items owned by current user
    items = Item.query.filter_by(owner_id=user_id).all()
    return render_template('table.html', items=items)


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

        if User.query.filter_by(username=username).first():
            return render_template('register.html', error='Username already exists')

        u = User(username=username, email=email, password_hash=generate_password_hash(password))
        db.session.add(u)
        db.session.commit()
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

        owner_id = session.get('user_id')
        # Enforce SKU uniqueness per-user
        if Item.query.filter_by(sku=sku, owner_id=owner_id).first():
            return render_template('form.html', error='SKU already exists for this user', action=url_for('create_item'))

        item_id = str(uuid.uuid4())
        it = Item(
            id=item_id,
            sku=sku,
            name=name,
            qty=int(qty) if qty.isdigit() else 0,
            location=location,
            category=category,
            description=description,
            purchase_price=purchase_price,
            owner_id=owner_id,
        )
        db.session.add(it)
        db.session.commit()
        return redirect(url_for('home_page'))

    return render_template('form.html', action=url_for('create_item'))


@app.route('/items/<item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    if 'user' not in session:
        return redirect(url_for('home'))
    item = Item.query.get(item_id)
    if not item:
        return redirect(url_for('home_page'))
    # only owner may edit
    if item.owner_id != session.get('user_id'):
        abort(403)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        qty = request.form.get('qty', '0')
        location = request.form.get('location', '').strip()
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        purchase_price_raw = request.form.get('purchase_price', '').strip()
        try:
            purchase_price = float(purchase_price_raw) if purchase_price_raw != '' else item.purchase_price
        except ValueError:
            purchase_price = item.purchase_price

        if not name:
            return render_template('form.html', error='Name required', item=item, action=url_for('edit_item', item_id=item_id))

        item.name = name
        item.qty = int(qty) if qty.isdigit() else 0
        item.location = location
        item.category = category
        item.description = description
        item.purchase_price = purchase_price
        db.session.commit()
        return redirect(url_for('home_page'))

    # GET
    # provide item and action (item is a model instance)
    return render_template('form.html', item=item, action=url_for('edit_item', item_id=item_id))


@app.route('/items/<item_id>/delete', methods=['POST'])
def delete_item(item_id):
    if 'user' not in session:
        return redirect(url_for('home'))
    owner_id = session.get('user_id')
    # check existence and ownership via lightweight query
    owner_row = Item.query.with_entities(Item.owner_id).filter_by(id=item_id).first()
    if not owner_row:
        return redirect(url_for('home_page'))
    if owner_row[0] != owner_id:
        abort(403)
    # perform a query-based delete to avoid instance/session attach issues
    Item.query.filter_by(id=item_id).delete()
    db.session.commit()
    return redirect(url_for('home_page'))

if __name__ == '__main__':
    # create DB tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=3000)
