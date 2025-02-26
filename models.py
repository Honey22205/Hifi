from flask_login import UserMixin
from app import db

class Customer(UserMixin, db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.Integer,unique=True, nullable=False) 
    password = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Customer {self.username}>'
    
    # Flask-Login required method
    def get_id(self):
        return self.id

class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)  
    phone = db.Column(db.Integer, unique=True, nullable=False) 

    def __repr__(self):
        return f'<Admin {self.username}>'
    
    def get_id(self):
        return self.id

class DeliveryAgent(UserMixin, db.Model):
    __tablename__ = 'delivery_agent'  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.Integer, unique=True, nullable=False) 
    password = db.Column(db.String(100), nullable=False)
    delivery_area = db.Column(db.String(100), nullable=False)  
    available_slots = db.Column(db.Boolean, nullable=False, default=True)


    
    def __repr__(self):
        return f'<DeliveryAgent {self.username}>'
    
    def get_id(self):
        return self.id
