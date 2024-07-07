'''from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///door.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the Flask application
db = SQLAlchemy(app)

login_manager = LoginManager(app) '''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///e-vendors.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Remove the initialization of db from here
# Initialize SQLAlchemy with the Flask application later in models.py

login_manager = LoginManager(app)

 

 
 