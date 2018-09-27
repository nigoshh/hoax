import copy
from application import app, db
from flask import redirect, render_template, request, url_for
from sqlalchemy import exc
from flask_login import login_required
from application.accounts.models import Account
from application.communities.models import Community
from application.communities.forms import (CommunityFormCreate,
                                           CommunityFormUpdate)


@app.route("/communities/new/")
def communities_form_create():
    return render_template("communities/new.html", form=CommunityFormCreate())


@app.route("/communities/", methods=["GET"])
def communities_list():
    return render_template("communities/list.html",
                           communities=Community.query.order_by("address"))


@app.route("/communities/", methods=["POST"])
def communities_create():
    form = CommunityFormCreate(request.form)

    if not form.validate():
        return render_template("communities/new.html", form=form)

    c = Community(form.address.data)

    db.session().add(c)
    db.session().commit()

    return redirect(url_for("communities_list"))


@app.route("/communities/<community_id>/", methods=["GET"])
@login_required
def communities_form_update(community_id):
    c = Community.query.get(community_id)
    form = CommunityFormUpdate()
    return render_template("communities/update.html", community=c, form=form)


@app.route("/communities/<community_id>/", methods=["POST"])
@login_required
def communities_update(community_id):
    c = Community.query.get(community_id)
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
        msg = "this address is already taken, please choose another one"
        form.address.errors.append(msg)
        return render_template("communities/update.html",
                               community=old_c, form=form)

    return redirect(url_for("communities_list"))


@app.route("/communities/<community_id>/delete", methods=["GET"])
@login_required
def communities_delete(community_id):
    Account.query.filter_by(community_id=community_id).delete()
    Community.query.filter_by(id=community_id).delete()
    db.session.commit()
    return redirect(url_for("communities_list"))
