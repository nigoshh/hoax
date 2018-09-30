import copy
from application import app, db
from flask import redirect, render_template, request, url_for
from sqlalchemy import exc
from flask_login import login_required
from passlib.hash import argon2
from application.accounts.models import Account
from application.accounts.forms import AccountFormCreate, AccountFormUpdate
from application.utils.form_utils import clean_pw


@app.route("/accounts/new/")
def accounts_form_create():
    form = AccountFormCreate()
    return render_template("accounts/new.html", form=form)


@app.route("/accounts/", methods=["GET"])
def accounts_list():
    return render_template("accounts/list.html",
                           accounts=Account.query.order_by("username"))


@app.route("/accounts/", methods=["POST"])
def accounts_create():
    form = AccountFormCreate(request.form)

    if not form.validate():
        clean_pw(form)
        return render_template("accounts/new.html", form=form)

    pw_hash = argon2.hash(form.password.data)
    clean_pw(form)

    a = Account(form.community.data.id, form.username.data, pw_hash,
                form.apartment.data, form.forename.data, form.surname.data,
                form.email.data, form.phone.data)

    try:
        db.session().add(a)
        db.session().commit()
    except exc.SQLAlchemyError as e:
        db.session().rollback()
        msg = "This username is already taken, please choose another one."
        form.username.errors.append(msg)
        return render_template("accounts/new.html", form=form)

    return redirect(url_for("accounts_single", account_id=a.id))


@app.route("/accounts/<account_id>/", methods=["GET"])
@login_required
def accounts_single(account_id):
    a = Account.query.get(account_id)
    return render_template("accounts/single.html", account=a)


@app.route("/accounts/<account_id>/update", methods=["GET"])
@login_required
def accounts_form_update(account_id):
    a = Account.query.get(account_id)
    form = AccountFormUpdate()
    form.community.data = a.community
    return render_template("accounts/update.html", account=a, form=form)


@app.route("/accounts/<account_id>/", methods=["POST"])
@login_required
def accounts_update(account_id):
    a = Account.query.get(account_id)
    old_a = copy.deepcopy(a)
    form = AccountFormUpdate(request.form)

    if not form.validate():
        clean_pw(form)
        return render_template("accounts/update.html", account=a, form=form)

    if not argon2.verify(form.current_pw.data, a.pw_hash):
        clean_pw(form)
        form.current_pw.errors.append("Wrong current password.")
        return render_template("accounts/update.html", account=a, form=form)

    if form.password.data:
        a.pw_hash = argon2.hash(form.password.data)

    clean_pw(form)

    for field in form:
        if field.data:
            setattr(a, field.name, field.data)

    try:
        db.session().commit()
    except exc.SQLAlchemyError as e:
        db.session().rollback()
        msg = "This username is already taken, please choose another one."
        form.username.errors.append(msg)
        return render_template("accounts/update.html",
                               account=old_a, form=form)

    return redirect(url_for("accounts_single", account_id=a.id))


@app.route("/accounts/<account_id>/delete", methods=["GET"])
@login_required
def accounts_delete_ask(account_id):
    a = Account.query.get(account_id)
    return render_template("accounts/delete.html", account=a)


@app.route("/accounts/<account_id>/delete", methods=["POST"])
@login_required
def accounts_delete(account_id):
    a = Account.query.get(account_id)
    db.session.delete(a)
    db.session.commit()
    return redirect(url_for("accounts_list"))
