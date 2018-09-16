from application import app, db
from flask import redirect, render_template, request, url_for
from application.users.models import User


@app.route("/users/new/")
def users_form_create():
    return render_template("users/new.html")


@app.route("/users/", methods=["GET"])
def users_list():
    return render_template("users/list.html", users=User.query.all())


@app.route("/users/", methods=["POST"])
def users_create():
    u = User(request.form.get("username"),
             request.form.get("full_name"),
             request.form.get("password"))

    db.session().add(u)
    db.session().commit()

    return redirect(url_for("users_list"))


@app.route("/users/<user_id>/", methods=["GET"])
def users_form_update(user_id):
    return render_template("users/update.html", user_id=user_id)


@app.route("/users/<user_id>/", methods=["POST"])
def users_update(user_id):
    u = User.query.get(user_id)

    u.username = request.form.get("username") or u.username
    if request.form.get("full_name"):
        u.full_name = request.form.get("full_name")
    if request.form.get("password"):
        u.pw_hash = request.form.get("password")

    db.session().commit()

    return redirect(url_for("users_list"))
