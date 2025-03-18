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
    created_at = db.Column(db.DateTime, default=func.now())
    
    
    addresses = db.relationship("Address", backref="customer", lazy=True)
    # Establish relationship with orders
    orders = db.relationship("Order", back_populates="user", foreign_keys="Order.user_id")  # Orders placed by the user


  
    
    def __repr__(self):
        return f'<Customer {self.username}>'
    
    # Flask-Login required method
    def get_id(self):
        return f"customer:{self.id}"
    

    
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
        return f"admin:{self.id}"

class DeliveryAgent(UserMixin, db.Model):
    __tablename__ = 'delivery_agent'  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.Integer, unique=True, nullable=False) 
    password = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=True, server_default='')
    bio = db.Column(db.Text, nullable=True, server_default='')
    delivery_area = db.Column(db.String(100), nullable=False)  
    available_slots = db.Column(db.Boolean, nullable=False, default=True)
    id_proof = db.Column(db.String(12), nullable=False, server_default='')
    is_approved = db.Column(db.Boolean, nullable=False, server_default='0')
    is_active = db.Column(db.Boolean, nullable=False, server_default='1')

    
    def __repr__(self):
        return f'<DeliveryAgent {self.username}>'
    
    def get_id(self):
        return f"delivery:{self.id}"
    

# Order Model
class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    delivery_agent_id = db.Column(db.Integer, db.ForeignKey('delivery_agent.id'), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="Pending")
    total_price = db.Column(db.Float, nullable=False)
    delivery_location = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now())
    delivered_at = db.Column(db.DateTime, nullable=True)

    delivery_status = db.Column(db.String(50),nullable=False, default="ActionPending")
    
    items = db.relationship("OrderItem", backref="order", lazy=True)
    user = db.relationship("Customer", back_populates="orders", foreign_keys=[user_id])  # Link to the user


    def __repr__(self):
        return f'<Order {self.id}, Status: {self.status}>'

# OrderItem Model
class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    menu_item = db.relationship("MenuItem", backref="order_items")

    def __repr__(self):
        return f'<OrderItem {self.id}, Order: {self.order_id}, Item: {self.menu_item_id}>'

# MenuItem Model
class MenuItem(db.Model):
    __tablename__ = 'menu_item'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<MenuItem {self.name}, Price: {self.price}>'

# Earnings Model
class Earnings(db.Model):
    __tablename__ = 'earnings'
    id = db.Column(db.Integer, primary_key=True)
    delivery_agent_id = db.Column(db.Integer, db.ForeignKey('delivery_agent.id'), nullable=False)
    base_pay = db.Column(db.Float, nullable=False, default=0.0)
    bonus = db.Column(db.Float, nullable=False, default=0.0)
    trips_count = db.Column(db.Integer, nullable=False, default=0)
    earned_at = db.Column(db.DateTime, default=func.now())
    
    # Relationship with DeliveryAgent
    delivery_agent = db.relationship('DeliveryAgent', backref='earnings')
    
    def __repr__(self):
        return f'<Earnings {self.delivery_agent_id} - {self.earned_at}>'
  
# Delivery agent feedback  
class DeliveryFeedback(db.Model):
    __tablename__ = 'delivery_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    delivery_agent_id = db.Column(db.Integer, db.ForeignKey('delivery_agent.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # e.g., a 1-5 scale rating
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now())
    
    # Relationships
    order = db.relationship("Order", backref=db.backref("delivery_feedbacks", lazy=True))
    delivery_agent = db.relationship("DeliveryAgent", backref=db.backref("delivery_feedbacks", lazy=True))
    
    def __repr__(self):
        return f'<DeliveryFeedback Order:{self.order_id} Agent:{self.delivery_agent_id} Rating:{self.rating}>'