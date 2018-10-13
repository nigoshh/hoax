from flask import Flask, render_template
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


from os import urandom
app.config["SECRET_KEY"] = urandom(32)

from flask_login import LoginManager, current_user
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth_login"
login_manager.login_message = "please login to use this functionality"


from functools import wraps

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user:
                return login_manager.unauthorized()

            if not current_user.is_authenticated:
                return login_manager.unauthorized()

            unauthorized = False

            if role != "ANY":
                unauthorized = True

                for user_role in current_user.roles():
                    if user_role == role:
                        unauthorized = False
                        break

            if unauthorized:
                return login_manager.unauthorized()

            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


from application import views

from application.auth import views

from application.accounts import models
from application.accounts import views

from application.bookings import models
from application.bookings import views

from application.communities import models
from application.communities import views

from application.invoices import models
from application.invoices import views

from application.resources import models
from application.resources import views


from application.accounts.models import Account

@login_manager.user_loader
def load_account(account_id):
    return Account.query.get(account_id)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", error=error), 404


try:
    db.create_all()
except:
    pass
