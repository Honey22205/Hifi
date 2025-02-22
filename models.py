# Creating sample database for testing

from flask_login import UserMixin # include this in model because it help to manage login state
from app import db

class Customer(UserMixin, db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.Integer, nullable=False) 
    password = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Customer {self.username}>'
    
    # this method is required for Flask-Login
    def get_id(self):
        return (self.id)