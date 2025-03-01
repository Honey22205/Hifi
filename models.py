from flask_login import UserMixin
from sqlalchemy import func
from app import db

class Customer(UserMixin, db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.Integer,unique=True, nullable=False) 
    password = db.Column(db.String(100), nullable=False)
    # address = db.Column(db.String(100), nullable=False)
    addresses = db.relationship("Address", backref="customer", lazy=True)

    # @staticmethod
    # def generate_id():
    #     """Generate an ID starting from '001'."""
    #     last_customer = db.session.query(func.max(db.cast(Customer.id, db.Integer))).scalar()
    #     next_id = int(last_customer) + 1 if last_customer else 1
    #     return f"{next_id:03}"  # Converts to '001', '002', etc.

    
    def __repr__(self):
        return f'<Customer {self.username}>'
    
    # Flask-Login required method
    def get_id(self):
        return self.id
    


    
class Address(db.Model):

    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    address_line = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    is_preferred = db.Column(db.Boolean, default=False)

    

    def __repr__(self):
        return f'<Address {self.address_line}>'

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
    id_proof = db.Column(db.String(12), nullable=False, server_default='')
    is_approved = db.Column(db.Boolean, nullable=False, server_default='0')
    is_active = db.Column(db.Boolean, nullable=False, server_default='1')

    
    def __repr__(self):
        return f'<DeliveryAgent {self.username}>'
    
    def get_id(self):
        return self.id
