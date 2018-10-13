import copy
from application import app, db, login_required
from flask import redirect, render_template, request, url_for
from sqlalchemy import exc
from application.invoices.models import Invoice
from application.invoices.forms import InvoiceFormCreate, InvoiceFormUpdate
from application.bookings.models import Booking

msg_unique = ("Some of the bookings you selected "
              "have already been added to another invoice.")
msg_paid = "Can't modify a paid invoice (uncheck \"paid\" to make changes)."
msg_same_account = ("All bookings in an invoice must"
                    " belong to the same account.")


@app.route("/invoices/new/")
@login_required()
def invoices_form_create():
    return render_template("invoices/new.html", form=InvoiceFormCreate())


@app.route("/invoices/", methods=["GET"])
@login_required()
def invoices_list():
    return render_template("invoices/list.html",
                           invoices=Invoice.query.order_by("date_created"))


@app.route("/invoices/", methods=["POST"])
@login_required()
def invoices_create():
    form = InvoiceFormCreate(request.form)

    if not form.validate():
        return render_template("invoices/new.html", form=form)

    # checking that all bookings belong to the same account
    if len(set([b.account.username for b in form.bookings.data])) > 1:
        form.bookings.errors.append(msg_same_account)
        return render_template("invoices/new.html", form=form)

    i = Invoice(form.bookings.data)

    try:
        db.session().add(i)
        db.session().commit()
    except exc.SQLAlchemyError as e:
        db.session().rollback()
        form.bookings.errors.append(msg_unique)
        return render_template("invoices/new.html", form=form)

    return redirect(url_for("invoices_single", invoice_id=i.id))


@app.route("/invoices/<invoice_id>/", methods=["GET"])
@login_required()
def invoices_single(invoice_id):
    i = Invoice.query.get(invoice_id)

    if not i:
        return render_template("404.html", res_type="invoice"), 404

    return render_template("invoices/single.html", invoice=i)


@app.route("/invoices/<invoice_id>/update", methods=["GET"])
@login_required()
def invoices_form_update(invoice_id):
    i = Invoice.query.get(invoice_id)

    if not i:
        return render_template("404.html", res_type="invoice"), 404

    form = InvoiceFormUpdate()
    form.bookings.query = Booking.get_allowed(invoice_id)
    form.bookings.data = i.bookings
    form.paid.data = i.paid
    return render_template("invoices/update.html", invoice=i, form=form)


@app.route("/invoices/<invoice_id>/", methods=["POST"])
@login_required()
def invoices_update(invoice_id):
    i = Invoice.query.get(invoice_id)

    if not i:
        return render_template("404.html", res_type="invoice"), 404

    old_i = copy.deepcopy(i)
    form = InvoiceFormUpdate(request.form)
    form.bookings.query = Booking.get_allowed(invoice_id)

    if not form.validate():
        return render_template("invoices/update.html", invoice=i, form=form)

    # checking that all bookings belong to the same account
    if len(set([b.account.username for b in form.bookings.data])) > 1:
        form.bookings.errors.append(msg_same_account)
        return render_template("invoices/update.html",
                               invoice=old_i, form=form)

    if i.paid and form.paid.data:
        form.bookings.errors.append(msg_paid)
        form.paid.errors.append(msg_paid)
        return render_template("invoices/update.html",
                               invoice=old_i, form=form)

    for field in form:
        setattr(i, field.name, field.data)
    i.calculate_price()

    try:
        db.session().commit()
    except exc.SQLAlchemyError as e:
        db.session().rollback()
        form.bookings.errors.append(msg_unique)
        return render_template("invoices/update.html",
                               invoice=old_i, form=form)

    return redirect(url_for("invoices_single", invoice_id=i.id))


@app.route("/invoices/<invoice_id>/delete", methods=["GET"])
@login_required()
def invoices_delete_ask(invoice_id):
    i = Invoice.query.get(invoice_id)

    if not i:
        return render_template("404.html", res_type="invoice"), 404

    return render_template("invoices/delete.html", invoice=i)


@app.route("/invoices/<invoice_id>/delete", methods=["POST"])
@login_required()
def invoices_delete(invoice_id):
    i = Invoice.query.get(invoice_id)

    if not i:
        return render_template("404.html", res_type="invoice"), 404

    db.session.delete(i)
    db.session.commit()
    return redirect(url_for("invoices_list"))
