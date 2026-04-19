from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login = LoginManager()
login.login_view = "auth.login"
login.login_message = "Please log in first."
