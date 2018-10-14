import copy
from decimal import Decimal, ROUND_DOWN
from application import app, db, login_manager, login_required
from flask import redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import exc
from application.resources.models import Resource
from application.resources.forms import ResourceFormCreate, ResourceFormUpdate


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
    resources = Resource.get_all()
    return render_template("resources/list.html", resources=resources)


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
