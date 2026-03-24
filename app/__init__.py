import os
from datetime import date
from flask import Flask, render_template, redirect, url_for
from config import Config
from app.extensions import db, login_manager
from flask_login import current_user, login_required
from app.extensions import mail


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Extensions
    mail.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
   

    # Ensure Instance Folder exists for the SQLite DB
    if not os.path.exists(app.instance_path):
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass

    # Create Database Tables
    with app.app_context():
        from app.models import User, Customer, Order, Complaint
        db.create_all()

    # Import Blueprints and the Search Form
    from app.auth.routes import auth_bp
    from app.customers.routes import customers_bp
    from app.orders.routes import orders_bp
    from app.complaints.routes import complaints_bp
    from app.customers.forms import CustomerSearchForm  

    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(orders_bp, url_prefix='/orders')
    app.register_blueprint(complaints_bp, url_prefix='/complaints')

    @app.route('/')
    @login_required
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))

        # 1. Initialize the Search Form for the Dashboard
        search_form = CustomerSearchForm()

        # 2. DATA FOR DASHBOARD SUMMARY CARDS
        today = date.today()
        total_today = Order.query.filter(db.func.date(Order.date_received) == today).count()
        ready_count = Order.query.filter_by(status='Ready').count()
        washing_count = Order.query.filter_by(status='Washing').count()
        open_complaints = Complaint.query.filter_by(status='Open').count()

        # 3. DATA FOR RECENT ORDERS TABLE
        recent_orders = Order.query.order_by(Order.date_received.desc()).limit(5).all()

        return render_template('dashboard.html', 
                               form=search_form, # Added this to the template context
                               total=total_today,
                               ready=ready_count,
                               washing=washing_count,
                               complaints=open_complaints,
                               recent_orders=recent_orders)

    return app