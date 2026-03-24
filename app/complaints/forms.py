from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

class ComplaintForm(FlaskForm):
    """Form to log and manage customer issues."""
    
    # What the customer says happened
    description = TextAreaField('Customer Complaint Details', 
        validators=[DataRequired()], 
        render_kw={"placeholder": "Describe the lost or damaged item..."})
    
    # Internal updates for the Admin
    internal_notes = TextAreaField('Internal Action/Notes (Optional)', 
        validators=[Optional()],
        render_kw={"placeholder": "e.g., Offered a 20% discount; investigating staff on shift."})
    
    # Matches the 'Open' -> 'In Progress' -> 'Resolved' workflow
    status = SelectField('Current Status', choices=[
        ('Open', 'Open / New'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved')
    ], default='Open')
    
    submit = SubmitField('Save Complaint')