import copy
from application import app, db, login_manager, login_required
from flask import redirect, render_template, request, url_for
from sqlalchemy import exc
from passlib.hash import argon2
from application.accounts.models import Account, ADMIN
from application.accounts.forms import AccountFormCreate, AccountFormUpdate
from application.utils.utils import clean_pw


@app.route("/accounts/new/")
def accounts_form_create():
    form = AccountFormCreate()
    return render_template("accounts/new.html", form=form)


@app.route("/accounts/", methods=["GET"])
@login_required(ADMIN)
def accounts_list():
    return render_template("accounts/list.html",
                           accounts=Account.list_with_debt())


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
@login_required()
def accounts_single(account_id):
    a = Account.query.get(account_id)

    if not a:
        return render_template("404.html", res_type="account"), 404

    if a.id not in [a.id for a in Account.get_allowed()]:
        return login_manager.unauthorized()

    return render_template("accounts/single.html", account=a)


@app.route("/accounts/<account_id>/update", methods=["GET"])
@login_required()
def accounts_form_update(account_id):
    a = Account.query.get(account_id)

    if not a:
        return render_template("404.html", res_type="account"), 404

    if a.id not in [a.id for a in Account.get_allowed()]:
        return login_manager.unauthorized()

    form = AccountFormUpdate()
    form.community.data = a.community
    form.admin_communities.data = a.admin_communities
    return render_template("accounts/update.html", account=a, form=form)


@app.route("/accounts/<account_id>/", methods=["POST"])
@login_required()
def accounts_update(account_id):
    a = Account.query.get(account_id)

    if not a:
        return render_template("404.html", res_type="account"), 404

    if a.id not in [a.id for a in Account.get_allowed()]:
        return login_manager.unauthorized()

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
    a.admin_communities = form.admin_communities.data

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
@login_required(ADMIN)
def accounts_delete_ask(account_id):
    a = Account.query.get(account_id)

    if not a:
        return render_template("404.html", res_type="account"), 404

    if a.id not in [a.id for a in Account.get_allowed()]:
        return login_manager.unauthorized()

    return render_template("accounts/delete.html", account=a)


@app.route("/accounts/<account_id>/delete", methods=["POST"])
@login_required(ADMIN)
def accounts_delete(account_id):
    a = Account.query.get(account_id)

    if not a:
        return render_template("404.html", res_type="account"), 404

    if a.id not in [a.id for a in Account.get_allowed()]:
        return login_manager.unauthorized()

    db.session.delete(a)
    db.session.commit()
    return redirect(url_for("accounts_list"))
