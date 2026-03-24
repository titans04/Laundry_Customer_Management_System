from datetime import datetime
from flask_login import UserMixin
from .extensions import db, login_manager # [cite: 4, 45, 59]

@login_manager.user_loader
def load_user(user_id):
    """Allows Flask-Login to load the Admin user by ID."""
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    """Admin logs into system [cite: 4, 45, 59]"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='Admin') # [cite: 58, 60]

class Customer(db.Model):
    """Customer arrives at store or is searched [cite: 3, 5, 20]"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) 
    email = db.Column(db.String(120), unique=True, nullable=False) 
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    
    # Relationships to track history [cite: 61, 62, 63]
    orders = db.relationship('Order', backref='customer', lazy=True)
    complaints = db.relationship('Complaint', backref='customer', lazy=True)

class Order(db.Model):
    """Admin creates order and updates processing [cite: 8, 25]"""
    id = db.Column(db.Integer, primary_key=True)
    service_type = db.Column(db.String(50), nullable=False) # [cite: 9, 26]
    item_description = db.Column(db.String(200)) # [cite: 26]
    quantity = db.Column(db.Integer, default=1) # [cite: 9, 26]
    
    # Status Workflow: Received -> Washing -> Drying -> Ready -> Collected [cite: 11, 14, 31-36]
    status = db.Column(db.String(20), default='Received') 
    total_price = db.Column(db.Float, nullable=False, default=0.0)
    
    date_received = db.Column(db.DateTime, default=datetime.utcnow)
    estimated_ready_time = db.Column(db.DateTime) # [cite: 10, 27]
    
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)

class Complaint(db.Model):
    """Complaint Handling Flow [cite: 43-50]"""
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False) # [cite: 49, 50]
    
    # Status: Open -> In Progress -> Resolved [cite: 51-57]
    internal_notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='Open') 
    
    date_logged = db.Column(db.DateTime, default=datetime.utcnow)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)