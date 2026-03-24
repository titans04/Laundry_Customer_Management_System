from flask import Blueprint, render_template, redirect, url_for, flash
from app.extensions import db
from app.models import User
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import LoginForm, RegistrationForm # Imported from your new forms.py

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If no admin exists yet, redirect to register 
    if User.query.count() == 0:
        return redirect(url_for('auth.register'))

    form = LoginForm()
    if form.validate_on_submit(): # Automatically checks for POST and field validity
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index')) # Goes to Dashboard
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Only allow registration if the database is empty 
    if User.query.count() > 0:
        flash("Admin already exists. Please login.", 'info')
        return redirect(url_for('auth.login'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Hash the password before saving
        hashed_password = generate_password_hash(form.password.data)
        new_admin = User(
            username=form.username.data, 
            password_hash=hashed_password, 
            role='Admin'
        )
        
        db.session.add(new_admin)
        db.session.commit()
        
        flash('Admin account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))