from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user
from passlib.hash import argon2
from application import app
from application.accounts.models import Account
from application.auth.forms import LoginForm
from application.utils.form_utils import clean_pw


@app.route("/auth/login", methods=["GET", "POST"])
def auth_login():
    if request.method == "GET":
        return render_template("auth/loginform.html", form=LoginForm())

    form = LoginForm(request.form)

    if not form.validate():
        clean_pw(form)
        return render_template("auth/loginform.html", form=form)

    a = Account.query.filter_by(username=form.username.data).first()

    if not a:
        clean_pw(form)
        return render_template("auth/loginform.html", form=form,
                               error="no such username or password")

    pw_match = argon2.verify(form.password.data, a.pw_hash)
    clean_pw(form)
    if not pw_match:
        return render_template("auth/loginform.html", form=form,
                               error="wrong password")

    login_user(a)
    return redirect(url_for("index"))


@app.route("/auth/logout")
def auth_logout():
    logout_user()
    return redirect(url_for("index"))
