from flask import Blueprint, render_template, redirect, url_for, flash, request
from app.extensions import db
from app.models import Customer, Order
from .forms import CustomerForm, CustomerSearchForm
from flask_login import login_required

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Main customer page with Search and List."""
    search_form = CustomerSearchForm()
    customers = Customer.query.order_by(Customer.id.desc()).all()
    
    if search_form.validate_on_submit():
        query = search_form.search_query.data
        customers = Customer.query.filter(
            (Customer.name.ilike(f'%{query}%')) | 
            (Customer.email.ilike(f'%{query}%')) |
            (Customer.phone.ilike(f'%{query}%'))
        ).all()

    return render_template('customers/index.html', form=search_form, customers=customers)

@customers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Route to add a new customer."""
    form = CustomerForm()
    if form.validate_on_submit():
        new_customer = Customer(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data
        )
        db.session.add(new_customer)
        db.session.commit()
        flash(f'Customer {new_customer.name} added successfully!', 'success')
        return redirect(url_for('customers.profile', customer_id=new_customer.id))
        
    return render_template('customers/add_customer.html', form=form)

@customers_bp.route('/<int:customer_id>')
@login_required
def profile(customer_id):
    """View a specific customer's details and their order history."""
    customer = Customer.query.get_or_404(customer_id)
    orders = customer.orders 
    return render_template('customers/profile.html', customer=customer, orders=orders)


# --- NEW: UPDATE CUSTOMER ROUTE ---
@customers_bp.route('/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def edit(customer_id):
    """Edit existing customer details."""
    customer = Customer.query.get_or_404(customer_id)
    # Pre-fill the form with existing data
    form = CustomerForm(obj=customer)
    
    if form.validate_on_submit():
        customer.name = form.name.data
        customer.email = form.email.data
        customer.phone = form.phone.data
        customer.address = form.address.data
        db.session.commit()
        flash('Customer details updated successfully!', 'success')
        return redirect(url_for('customers.profile', customer_id=customer.id))
        
    return render_template('customers/add_customer.html', form=form, title="Edit Customer")

# --- NEW: DELETE CUSTOMER ROUTE ---
@customers_bp.route('/delete/<int:customer_id>', methods=['POST'])
@login_required
def delete(customer_id):
    """Delete a customer and their associated orders."""
    customer = Customer.query.get_or_404(customer_id)
    
    # Optional: Logic to handle what happens to their orders
    # If your model uses cascade delete, orders go away automatically.
    db.session.delete(customer)
    db.session.commit()
    flash(f'Customer {customer.name} has been removed.', 'info')
    return redirect(url_for('customers.index'))