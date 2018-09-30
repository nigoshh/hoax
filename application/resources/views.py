import copy
from application import app, db
from flask import redirect, render_template, request, url_for
from sqlalchemy import exc
from flask_login import login_required
from application.resources.models import Resource
from application.resources.forms import ResourceFormCreate, ResourceFormUpdate


def msg_unique_atn_1(form):
    return ("%s number %d already exists at address %s."
            % (form.type.data.capitalize(), form.number.data,
               form.address.data))


msg_unique_atn_2 = "Please change either address, type or number."


@app.route("/resources/new/")
@login_required
def resources_form_create():
    form = ResourceFormCreate()
    return render_template("resources/new.html", form=form)


@app.route("/resources/", methods=["GET"])
def resources_list():
    return render_template("resources/list.html",
                           resources=Resource.query.order_by("address"))


@app.route("/resources/", methods=["POST"])
@login_required
def resources_create():
    form = ResourceFormCreate(request.form)

    if not form.validate():
        return render_template("resources/new.html", form=form)

    r = Resource(form.address.data, form.type.data, form.number.data,
                 form.price.data, form.communities.data)

    try:
        db.session().add(r)
        db.session().commit()
    except exc.SQLAlchemyError as e:
        db.session().rollback()
        for field in [form.address, form.type, form.number]:
            field.errors.extend([msg_unique_atn_1(form), msg_unique_atn_2])
        return render_template("resources/new.html", form=form)

    return redirect(url_for("resources_single", resource_id=r.id))


@app.route("/resources/<resource_id>/", methods=["GET"])
@login_required
def resources_single(resource_id):
    r = Resource.query.get(resource_id)
    return render_template("resources/single.html", resource=r)


@app.route("/resources/<resource_id>/update", methods=["GET"])
@login_required
def resources_form_update(resource_id):
    r = Resource.query.get(resource_id)
    form = ResourceFormUpdate()
    form.communities.data = r.communities
    return render_template("resources/update.html", resource=r, form=form)


@app.route("/resources/<resource_id>/", methods=["POST"])
@login_required
def resources_update(resource_id):
    r = Resource.query.get(resource_id)
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
        for field in [form.address, form.type, form.number]:
            field.errors.extend([msg_unique_atn_1(form), msg_unique_atn_2])
        return render_template("resources/update.html",
                               resource=old_r, form=form)

    return redirect(url_for("resources_single", resource_id=r.id))


@app.route("/resources/<resource_id>/delete", methods=["GET"])
@login_required
def resources_delete_ask(resource_id):
    r = Resource.query.get(resource_id)
    return render_template("resources/delete.html", resource=r)


@app.route("/resources/<resource_id>/delete", methods=["POST"])
@login_required
def resources_delete(resource_id):
    r = Resource.query.get(resource_id)
    db.session.delete(r)
    db.session.commit()
    return redirect(url_for("resources_list"))
