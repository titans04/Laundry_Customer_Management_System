from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models import Complaint, Customer
from .forms import ComplaintForm

complaints_bp = Blueprint('complaints', __name__)

@complaints_bp.route('/')
@login_required
def index():
    all_complaints = Complaint.query.order_by(Complaint.date_logged.desc()).all()
    return render_template('complaints/index.html', complaints=all_complaints)

@complaints_bp.route('/add/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def add(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    form = ComplaintForm()
    if form.validate_on_submit():
        new_complaint = Complaint(
            description=form.description.data,
            internal_notes=form.internal_notes.data,
            status=form.status.data,
            customer_id=customer.id
        )
        db.session.add(new_complaint)
        db.session.commit()
        flash(f'Complaint logged for {customer.name}.', 'warning')
        return redirect(url_for('customers.profile', customer_id=customer.id))
    return render_template('complaints/add_complaint.html', form=form, customer=customer)

# NEW MULTI-STATUS ROUTE
@complaints_bp.route('/update_status/<int:complaint_id>/<string:new_status>')
@login_required
def update_status(complaint_id, new_status):
    complaint = Complaint.query.get_or_404(complaint_id)
    if new_status in ['Open', 'In Progress', 'Resolved']:
        complaint.status = new_status
        db.session.commit()
        flash(f'Complaint updated to {new_status}.', 'info')
    return redirect(request.referrer or url_for('complaints.index'))

@complaints_bp.route('/delete/<int:complaint_id>', methods=['POST'])
@login_required
def delete(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    db.session.delete(complaint)
    db.session.commit()
    flash('Complaint record removed.', 'danger')
    return redirect(url_for('complaints.index'))