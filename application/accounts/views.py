import copy
from application import app, db
from flask import redirect, render_template, request, url_for
from sqlalchemy import exc
from flask_login import login_required
from passlib.hash import argon2
from application.accounts.models import Account
from application.accounts.forms import AccountFormCreate, AccountFormUpdate
from application.communities.models import Community
from application.utils.form_utils import clean_pw


def update_community_choices(form):
    form.community_id.choices = [(c.id, c.address)
                                 for c in Community.query.order_by("address")]


@app.route("/accounts/new/")
def accounts_form_create():
    form = AccountFormCreate()
    update_community_choices(form)
    return render_template("accounts/new.html", form=form)


@app.route("/accounts/", methods=["GET"])
def accounts_list():
    return render_template("accounts/list.html",
                           accounts=Account.query.order_by("username"))


@app.route("/accounts/", methods=["POST"])
def accounts_create():
    form = AccountFormCreate(request.form)
    update_community_choices(form)

    if not form.validate():
        clean_pw(form)
        return render_template("accounts/new.html", form=form)

    pw_hash = argon2.hash(form.password.data)
    clean_pw(form)

    a = Account(form.community_id.data, form.username.data, pw_hash,
                form.apartment.data, form.forename.data, form.surname.data)

    try:
        db.session().add(a)
        db.session().commit()
    except exc.SQLAlchemyError as e:
        msg = "this username is already taken, please choose another one"
        form.username.errors.append(msg)
        return render_template("accounts/new.html", form=form)

    return redirect(url_for("accounts_list"))


@app.route("/accounts/<account_id>/", methods=["GET"])
@login_required
def accounts_form_update(account_id):
    a = Account.query.get(account_id)
    form = AccountFormUpdate()
    update_community_choices(form)
    form.community_id.data = a.community_id
    return render_template("accounts/update.html", account=a, form=form)


@app.route("/accounts/<account_id>/", methods=["POST"])
@login_required
def accounts_update(account_id):
    a = Account.query.get(account_id)
    old_a = copy.deepcopy(a)
    form = AccountFormUpdate(request.form)
    update_community_choices(form)

    if not form.validate():
        clean_pw(form)
        return render_template("accounts/update.html", account=a, form=form)

    if not argon2.verify(form.old_pw.data, a.pw_hash):
        clean_pw(form)
        form.old_pw.errors.append("wrong old password")
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
        msg = "this username is already taken, please choose another one"
        form.username.errors.append(msg)
        return render_template("accounts/update.html",
                               account=old_a, form=form)

    return redirect(url_for("accounts_list"))


@app.route("/accounts/<account_id>/delete", methods=["GET"])
@login_required
def accounts_delete(account_id):
    Account.query.filter_by(id=account_id).delete()
    db.session.commit()
    return redirect(url_for("accounts_list"))
