from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

import os

if os.environ.get("HEROKU"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
else:
    # three slashes mean that the file is in the same folder where all
    # the application's files are
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hoax.db"
    # configure SQLAlchemy to print all SQL queries
    app.config["SQLALCHEMY_ECHO"] = True
# disable a deprecated option
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# object which we use to access the database
db = SQLAlchemy(app)

from application import views
from application.users import models
from application.users import views

try:
    db.create_all()
except:
    pass
