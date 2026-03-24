from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    """Used for the one-time Admin setup."""
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=50)])
    password = PasswordField('Password', 
                             validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register Admin')

    def validate_username(self, username):
        """Check if username is already taken (extra safety)."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')



class LoginForm(FlaskForm):
    """Used for daily Admin login to reach the Dashboard."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')