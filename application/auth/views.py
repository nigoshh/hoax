from urllib.parse import urlparse, urljoin
from flask import abort, render_template, request, redirect, url_for
from flask_login import login_user, logout_user
from passlib.hash import argon2
from application import app, login_manager
from application.accounts.models import Account
from application.auth.forms import LoginForm
from application.utils.form_utils import clean_pw


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ('http', 'https') and
            ref_url.netloc == test_url.netloc)


@app.route("/auth/login", methods=["GET", "POST"])
def auth_login():
    next = request.args.get("next")

    if request.method == "GET":
        form = LoginForm()
        if next:
            return render_template("auth/loginform.html", form=form, next=next,
                                   message=login_manager.login_message)
        return render_template("auth/loginform.html", form=form)

    form = LoginForm(request.form)

    if not form.validate():
        clean_pw(form)
        return render_template("auth/loginform.html", form=form)

    a = Account.query.filter_by(username=form.username.data).first()

    if not a:
        clean_pw(form)
        for field in [form.username, form.password]:
            field.errors.append("No such username or password.")
        return render_template("auth/loginform.html", form=form)

    pw_match = argon2.verify(form.password.data, a.pw_hash)
    clean_pw(form)
    if not pw_match:
        form.password.errors.append("Wrong password.")
        return render_template("auth/loginform.html", form=form)

    login_user(a)

    if not is_safe_url(next):
        return abort(400)

    return redirect(next or url_for("index"))


@app.route("/auth/logout")
def auth_logout():
    logout_user()
    return redirect(url_for("index"))
