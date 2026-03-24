from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional
from app.models import Customer

class CustomerSearchForm(FlaskForm):
    """Admin searches for an existing customer by name, email, or phone."""
    search_query = StringField('Search (Name, Email, or Phone)', validators=[DataRequired()])
    submit = SubmitField('Search')

class CustomerForm(FlaskForm):
    """Form to register a brand new customer."""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    
    # Added Email() validator and Optional() so it's not required, 
    # but IF they type one, it must be a valid format.
    email = StringField('Email Address') 
    
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField('Address (Optional)')
    submit = SubmitField('Register Customer')

    def validate_phone(self, phone):
        """Custom check: Prevents double-registering the same phone number."""
        customer = Customer.query.filter_by(phone=phone.data).first()
        if customer:
            raise ValidationError('This phone number is already registered to another customer.')

    # NEW: Email Uniqueness Check
    def validate_email(self, email):
        """Custom check: Prevents double-registering the same email address."""
        if email.data: # Only check if the user actually typed something in the email field
            customer = Customer.query.filter_by(email=email.data).first()
            if customer:
                raise ValidationError('This email address is already registered to another customer.')