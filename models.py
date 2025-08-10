from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    available = db.Column(db.Boolean, default=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    owner = db.relationship('User', backref=db.backref('books', lazy=True))

class Borrow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrow_date = db.Column(db.DateTime, default=datetime.utcnow)
    return_date = db.Column(db.DateTime)
    returned = db.Column(db.Boolean, default=False)
    
    book = db.relationship('Book', backref=db.backref('borrows', lazy=True))
    user = db.relationship('User', backref=db.backref('borrows', lazy=True))