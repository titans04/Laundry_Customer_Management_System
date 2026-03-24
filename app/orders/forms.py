from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, TextAreaField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired, NumberRange

class OrderForm(FlaskForm):
    """
    Form for creating a new laundry order.
    Includes Estimated Ready Time to prevent giving out wet clothes.
    """
    
    # 1. Service Selection (Fixed pricing in the backend)
    service_type = SelectField('Service Type', choices=[
        ('Full Wash', 'Full Wash & Fold (R150.00)'),
        ('Ironing', 'Ironing Only (R80.00)'),
        ('Dry Clean', 'Dry Cleaning (R250.00)'),
        ('Blankets', 'Blankets/Duvets (R180.00)')
    ], validators=[DataRequired()])
    
    # 2. Item Description (Prevents mix-ups)
    item_description = StringField('Item Description', 
        validators=[DataRequired()], 
        render_kw={"placeholder": "e.g., 5 Blue Shirts, 2 Denim Jeans"})
    
    # 3. Quantity (For automatic price calculation)
    quantity = IntegerField('Quantity / Number of Bags', 
        default=1, 
        validators=[DataRequired(), NumberRange(min=1, message="Must be at least 1")])

    # 4. NEW: Estimated Ready Time (Solves the Wet Clothes problem)
    estimated_ready_time = DateTimeLocalField(
        'Estimated Ready Time', 
        format='%Y-%m-%dT%H:%M', 
        validators=[DataRequired()],
        render_kw={"class": "form-control", "type": "datetime-local"}
    )
    
    # 5. Special Instructions
    notes = TextAreaField('Special Instructions', 
        render_kw={"placeholder": "e.g., Use extra softener, handle with care"})

    submit = SubmitField('Confirm & Create Order')