import copy
from application import app, db, login_manager, login_required
from flask import redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import exc
from application.accounts.models import ADMIN
from application.communities.models import Community
from application.communities.forms import (CommunityFormCreate,
                                           CommunityFormUpdate)


@app.route("/communities/new/")
def communities_form_create():
    return render_template("communities/new.html", form=CommunityFormCreate())


@app.route("/communities/", methods=["GET"])
def communities_list():
    return render_template("communities/list.html",
                           communities=Community.list_with_stats())


@app.route("/communities/", methods=["POST"])
def communities_create():
    form = CommunityFormCreate(request.form)

    if not form.validate():
        return render_template("communities/new.html", form=form)

    c = Community(form.address.data)

    try:
        db.session().add(c)
        db.session().commit()
    except exc.SQLAlchemyError as e:
        db.session().rollback()
        msg = "This address is already taken, please choose another one."
        form.address.errors.append(msg)
        return render_template("communities/new.html", form=form)

    if current_user.is_authenticated and ADMIN in current_user.roles():
        return redirect(url_for("communities_single", community_id=c.id))

    return redirect(url_for("communities_list"))


@app.route("/communities/<community_id>/", methods=["GET"])
@login_required()
def communities_single(community_id):
    c = Community.query.get(community_id)

    if not c:
        return render_template("404.html", res_type="community"), 404

    show_accounts = False
    if c.id in [c.id for c in Community.get_allowed()]:
        show_accounts = True

    return render_template("communities/single.html",
                           community=c, show_accounts=show_accounts)


@app.route("/communities/<community_id>/update", methods=["GET"])
@login_required(ADMIN)
def communities_form_update(community_id):
    c = Community.query.get(community_id)

    if not c:
        return render_template("404.html", res_type="community"), 404

    if c.id not in [c.id for c in Community.get_allowed()]:
        return login_manager.unauthorized()

    form = CommunityFormUpdate()
    return render_template("communities/update.html", community=c, form=form)


@app.route("/communities/<community_id>/", methods=["POST"])
@login_required(ADMIN)
def communities_update(community_id):
    c = Community.query.get(community_id)

    if not c:
        return render_template("404.html", res_type="community"), 404

    if c.id not in [c.id for c in Community.get_allowed()]:
        return login_manager.unauthorized()

    old_c = copy.deepcopy(c)
    form = CommunityFormUpdate(request.form)

    if not form.validate():
        return render_template("communities/update.html",
                               community=c, form=form)

    if form.address.data:
        c.address = form.address.data

    try:
        db.session().commit()
    except exc.SQLAlchemyError as e:
        db.session().rollback()
        msg = "This address is already taken, please choose another one."
        form.address.errors.append(msg)
        return render_template("communities/update.html",
                               community=old_c, form=form)

    return redirect(url_for("communities_single", community_id=c.id))


@app.route("/communities/<community_id>/delete", methods=["GET"])
@login_required()
def communities_delete_ask(community_id):
    c = Community.query.get(community_id)

    if not c:
        return render_template("404.html", res_type="community"), 404

    if c.id not in [c.id for c in Community.get_allowed()]:
        return login_manager.unauthorized()

    return render_template("communities/delete.html", community=c)


@app.route("/communities/<community_id>/delete", methods=["POST"])
@login_required()
def communities_delete(community_id):
    c = Community.query.get(community_id)

    if not c:
        return render_template("404.html", res_type="community"), 404

    if c.id not in [c.id for c in Community.get_allowed()]:
        return login_manager.unauthorized()

    db.session.delete(c)
    db.session.commit()
    return redirect(url_for("communities_list"))
