import copy
from decimal import Decimal, ROUND_DOWN
from application import app, db, login_manager, login_required
from flask import redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import exc
from werkzeug.urls import url_encode
from application.resources.models import Resource
from application.resources.forms import (
    ResourceFormCreate, ResourceFormFilter, ResourceFormUpdate)


def msg_unique_atn_1(form):
    return ("%s %s already exists at address %s."
            % (form.type.data.capitalize(), form.name.data,
               form.address.data))


msg_unique_atn_2 = "Please change either address, type or name/identifier."


@app.route("/resources/new/")
@login_required()
def resources_form_create():
    form = ResourceFormCreate()
    return render_template("resources/new.html", form=form)


@app.route("/resources/", methods=["GET"])
def resources_list():
    form = ResourceFormFilter(request.args)

    if not form.validate():
        resources = (Resource.query
                     .order_by(Resource.address, Resource.type, Resource.name)
                     .paginate(1, app.config["ITEMS_PER_PAGE"], False))
        return render_template(
            "resources/list.html", resources=resources.items, form=form,
            pagination=resources,
            url_for_pagination=(url_for("resources_list") + "?page="))

    page = request.args.get("page", 1, type=int)
    qs_params = request.args.to_dict(flat=False)
    qs_params.pop("page", None)
    url_for_pagination = ("%s?%s" % (url_for("resources_list"),
                                     url_encode(qs_params)))
    if len(qs_params) > 0:
        url_for_pagination += "&"
    url_for_pagination += "page="

    query_filter = {}
    if ("column" in qs_params and "keyword" in qs_params
       and qs_params["column"][0] and qs_params["keyword"][0]):
        query_filter[qs_params["column"][0]] = qs_params["keyword"][0]

    resources = (Resource.query
                 .filter_by(**query_filter)
                 .order_by(Resource.address, Resource.type, Resource.name)
                 .paginate(page, app.config["ITEMS_PER_PAGE"], False))

    return render_template(
        "resources/list.html", resources=resources.items, form=form,
        pagination=resources, url_for_pagination=url_for_pagination)


@app.route("/resources/", methods=["POST"])
@login_required()
def resources_create():
    form = ResourceFormCreate(request.form)

    if not form.validate():
        return render_template("resources/new.html", form=form)

    r = Resource(current_user.get_id(),
                 form.address.data, form.type.data, form.name.data,
                 form.price.data.quantize(Decimal('.01'), rounding=ROUND_DOWN),
                 form.communities.data)

    try:
        db.session().add(r)
        db.session().commit()
    except exc.SQLAlchemyError as e:
        db.session().rollback()
        for field in [form.address, form.type, form.name]:
            field.errors.extend([msg_unique_atn_1(form), msg_unique_atn_2])
        return render_template("resources/new.html", form=form)

    return redirect(url_for("resources_single", resource_id=r.id))


@app.route("/resources/<resource_id>/", methods=["GET"])
def resources_single(resource_id):
    r = Resource.query.get(resource_id)

    if not r:
        return render_template("404.html", res_type="resource"), 404

    return render_template("resources/single.html", resource=r)


@app.route("/resources/<resource_id>/update", methods=["GET"])
@login_required()
def resources_form_update(resource_id):
    r = Resource.query.get(resource_id)

    if not r:
        return render_template("404.html", res_type="resource"), 404

    if r.account_id != current_user.get_id():
        return login_manager.unauthorized()

    form = ResourceFormUpdate()
    form.communities.data = r.communities
    return render_template("resources/update.html", resource=r, form=form)


@app.route("/resources/<resource_id>/", methods=["POST"])
@login_required()
def resources_update(resource_id):
    r = Resource.query.get(resource_id)

    if not r:
        return render_template("404.html", res_type="resource"), 404

    if r.account_id != current_user.get_id():
        return login_manager.unauthorized()

    old_r = copy.deepcopy(r)
    form = ResourceFormUpdate(request.form)

    if not form.validate():
        return render_template("resources/update.html", resource=r, form=form)

    for field in form:
        if field.data or (field.name == "communities"):
            setattr(r, field.name, field.data)

    try:
        db.session().commit()
    except exc.SQLAlchemyError as e:
        db.session().rollback()
        for field in [form.address, form.type, form.name]:
            field.errors.extend([msg_unique_atn_1(form), msg_unique_atn_2])
        return render_template("resources/update.html",
                               resource=old_r, form=form)

    return redirect(url_for("resources_single", resource_id=r.id))


@app.route("/resources/<resource_id>/delete", methods=["GET"])
@login_required()
def resources_delete_ask(resource_id):
    r = Resource.query.get(resource_id)

    if not r:
        return render_template("404.html", res_type="resource"), 404

    if r.account_id != current_user.get_id():
        return login_manager.unauthorized()

    return render_template("resources/delete.html", resource=r)


@app.route("/resources/<resource_id>/delete", methods=["POST"])
@login_required()
def resources_delete(resource_id):
    r = Resource.query.get(resource_id)

    if not r:
        return render_template("404.html", res_type="resource"), 404

    if r.account_id != current_user.get_id():
        return login_manager.unauthorized()

    db.session.delete(r)
    db.session.commit()
    return redirect(url_for("resources_list"))
