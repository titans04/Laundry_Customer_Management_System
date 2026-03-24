from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app # Added current_app
from flask_login import login_required
from app.extensions import db, mail
from app.models import Order, Customer
from .forms import OrderForm
from datetime import datetime
from flask_mail import Message

orders_bp = Blueprint('orders', __name__)

# --- PRICING CONFIGURATION ---
PRICES = {
    'Full Wash': 150.00,
    'Ironing': 80.00,
    'Dry Clean': 250.00,
    'Blankets': 180.00
}

@orders_bp.route('/')
@login_required
def index():
    """Master list of all orders to track shop progress."""
    all_orders = Order.query.order_by(Order.date_received.desc()).all()
    return render_template('orders/index.html', orders=all_orders)

@orders_bp.route('/create/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def create(customer_id):
    """Link an order to a specific customer ID and set a ready-time promise."""
    customer = Customer.query.get_or_404(customer_id)
    form = OrderForm()
    
    if form.validate_on_submit():
        # 1. AUTOMATIC PRICING LOGIC
        service = form.service_type.data
        unit_price = PRICES.get(service, 0.0)
        total = unit_price * form.quantity.data

        # 2. CREATE THE ORDER OBJECT
        new_order = Order(
            service_type=service,
            item_description=form.item_description.data,
            quantity=form.quantity.data,
            total_price=total,
            status='Received',
            estimated_ready_time=form.estimated_ready_time.data,
            customer_id=customer.id,
            date_received=datetime.utcnow()
        )
        
        # 3. SAVE TO DATABASE
        db.session.add(new_order)
        db.session.commit()
        
        # 4. FEEDBACK
        flash(f'Order #{new_order.id} created! Total: R{total:.2f}.', 'success')
        return redirect(url_for('customers.profile', customer_id=customer.id))
        
    return render_template('orders/create_order.html', form=form, customer=customer)

@orders_bp.route('/update_status/<int:order_id>/<string:new_status>')
@login_required
def update_status(order_id, new_status):
    order = Order.query.get_or_404(order_id)
    order.status = new_status
    
    # 1. Update the timestamp if Ready
    if new_status == 'Ready':
        order.estimated_ready_time = datetime.utcnow()
    
    # 2. SAVE TO DATABASE IMMEDIATELY (Unlocks SQLite)
    try:
        db.session.commit()
        flash(f'Order #{order.id} status updated to {new_status}.', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('orders.index'))

    # 3. TRIGGER THE EMAIL
    if new_status == 'Ready' and order.customer.email:
        try:
            # Using current_app to safely get your config settings
            sender_email = current_app.config.get('MAIL_USERNAME')
            
            msg = Message(
                subject=f"Laundry Order #{order.id} is Ready! 🧺",
                sender=sender_email,
                recipients=[order.customer.email]
            )
            msg.body = f"Hi {order.customer.name},\n\nYour laundry order ({order.service_type}) is ready! Amount: R{order.total_price:.2f}."
            
            mail.send(msg)
            flash(f'Notification sent to {order.customer.email}.', 'success')
        except Exception as e:
            flash(f'Order updated, but email failed. Check internet/config.', 'warning')

    return redirect(request.referrer or url_for('orders.index'))