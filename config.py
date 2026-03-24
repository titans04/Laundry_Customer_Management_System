import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # --- SECURITY ---
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # --- DATABASE ---
    # This points to your instance/app.db file
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- MAIL SETTINGS ---
    # These are required for the email notification logic to work
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    
    # Use environment variables for safety, or hardcode your laundry email for the demo
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your-laundry-email@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your-app-password'
    
    # Set to True if you want to test the app without actually sending emails
    MAIL_SUPPRESS_SEND = False