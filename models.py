from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"


class Item(db.Model):
    id = db.Column(db.String(36), primary_key=True)  # keep UUID string
    sku = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    qty = db.Column(db.Integer, default=0)
    location = db.Column(db.String(200))
    category = db.Column(db.String(200))
    description = db.Column(db.Text)
    purchase_price = db.Column(db.Float, default=0.0)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref='items')

    __table_args__ = (
        db.UniqueConstraint('owner_id', 'sku', name='uix_owner_sku'),
    )

    def __repr__(self):
        return f"<Item {self.sku} ({self.id})>"
