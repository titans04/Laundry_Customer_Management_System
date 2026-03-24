from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail


# Initialize the extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

# Optional: Tell LoginManager where the login page is for @login_required
login_manager.login_view = 'auth.login'

