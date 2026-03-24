from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db, mail
from app.models import Order, Customer
from .forms import OrderForm
from datetime import datetime
from flask_mail import Message


orders_bp = Blueprint('orders', __name__)

# --- PRICING CONFIGURATION ---
# This stops employees from charging wrong prices. 
# The system does the math!
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
    
    # Prices locked in backend to prevent employee errors
    PRICES = {
        'Full Wash': 150.00,
        'Ironing': 80.00,
        'Dry Clean': 250.00,
        'Blankets': 180.00
    }
    
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
            # NEW: Saving the date/time promised to the customer
            estimated_ready_time=form.estimated_ready_time.data,
            customer_id=customer.id,
            date_received=datetime.utcnow()
        )
        
        # 3. SAVE TO DATABASE
        db.session.add(new_order)
        db.session.commit()
        
        # 4. FEEDBACK
        flash(f'Order #{new_order.id} created! Total: R{total:.2f}. Ready by: {new_order.estimated_ready_time.strftime("%d %b %H:%M")}', 'success')
        
        return redirect(url_for('customers.profile', customer_id=customer.id))
        
    return render_template('orders/create_order.html', form=form, customer=customer)



@orders_bp.route('/update_status/<int:order_id>/<string:new_status>')
@login_required
def update_status(order_id, new_status):
    order = Order.query.get_or_404(order_id)
    order.status = new_status
    
    if new_status == 'Ready':
        # 1. Update timestamp
        order.estimated_ready_time = datetime.utcnow()
        
        # 2. TRIGGER THE EMAIL
        try:
            msg = Message(
                subject=f"Laundry Order #{order.id} is Ready!",
                sender="noreply@laundrysystem.co.za",
                recipients=[order.customer.email]
            )
            msg.body = f"""
            Hi {order.customer.name},

            Great news! Your laundry order ({order.service_type}) is ready for collection.
            
            Total Amount Due: R{order.total_price:.2f}
            
            Please visit us during shop hours to collect your items.
            
            Thank you for choosing our service!
            """
            mail.send(msg)
            flash(f'Order #{order.id} is Ready. Notification email sent to {order.customer.email}.', 'success')
        except Exception as e:
            flash(f'Order marked as Ready, but email failed: {str(e)}', 'danger')

    db.session.commit()
    return redirect(request.referrer or url_for('orders.index'))