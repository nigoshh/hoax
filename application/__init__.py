from flask import Flask, render_template
app = Flask(__name__)


# database connectivity and ORM
from flask_sqlalchemy import SQLAlchemy
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

db = SQLAlchemy(app)


# login functionality
from os import urandom
app.config["SECRET_KEY"] = urandom(32)

from flask_login import LoginManager, current_user
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth_login"
login_manager.login_message = ("Please log in to access this page. "
                               "If you're already logged in and still seeing "
                               "this message, it means you don't have enough "
                               "privileges to access this page. If you're "
                               "trying to edit a booking you should be able "
                               "to access, make sure that it isn't already "
                               "been added to an invoice (in that case you "
                               "have to remove it from the invoice to be able "
                               "to edit it).")


# roles in login_required
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


# load application content
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


# login functionality, part 2
from application.accounts.models import Account

@login_manager.user_loader
def load_account(account_id):
    return Account.query.get(account_id)


# custom 404 template
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", error=error), 404


# maximum number of items per page (for lists)
app.config["ITEMS_PER_PAGE"] = 10

# database creation
try:
    db.create_all()
except:
    pass
