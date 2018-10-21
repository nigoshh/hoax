import copy
from datetime import datetime as dt
from application import app, db, login_manager, login_required
from flask import redirect, render_template, request, url_for
from flask_login import current_user
from application.accounts.models import ADMIN
from application.bookings.models import Booking
from application.bookings.forms import (BookingFormCreate, BookingFormFilter,
                                        BookingFormUpdate)


def msg_free_rts_1(resource):
    return "Resource %s is already booked in this time slot." % resource


msg_free_rts_2 = "Please check the bookings' list to find a free time slot."
msg_past = "Booking starting date/time can't be in the past."
msg_start = "Starting time must be before ending time."
msg_end = "Ending time must be after starting time."
msg_from = "\"From\" date/time must be before \"to\" date/time."
msg_to = "\"To\" date/time must be after \"from\" date/time."
msg_both_from_date = ("If you specify \"from (date)\", "
                      "you must specify also \"from (time)\".")
msg_both_from_time = ("If you specify \"from (time)\", "
                      "you must specify also \"from (date)\".")
msg_both_to_date = ("If you specify \"to (date)\", "
                    "you must specify also \"to (time)\".")
msg_both_to_time = ("If you specify \"to (time)\" "
                    "you must specify also \"to (date)\".")


@app.route("/bookings/new/")
@login_required()
def bookings_form_create():
    form = BookingFormCreate()
    return render_template("bookings/new.html", form=form)


@app.route("/bookings/", methods=["GET"])
@login_required()
def bookings_list():
    form = BookingFormFilter(request.args)
    form.validate()

    from_dt = None
    if (form.from_date.data or form.from_time.data):
        if (form.from_date.data and form.from_time.data):
            from_dt = dt.combine(form.from_date.data, form.from_time.data)
        elif form.from_date.data:
            form.from_date.errors.append(msg_both_from_date)
            form.from_time.errors.append(msg_both_from_date)
        else:
            form.from_date.errors.append(msg_both_from_time)
            form.from_time.errors.append(msg_both_from_time)
    to_dt = None
    if (form.to_date.data or form.to_time.data):
        if (form.to_date.data and form.to_time.data):
            to_dt = dt.combine(form.to_date.data, form.to_time.data)
        elif form.to_date.data:
            form.to_date.errors.append(msg_both_to_date)
            form.to_time.errors.append(msg_both_to_date)
        else:
            form.to_date.errors.append(msg_both_to_time)
            form.to_time.errors.append(msg_both_to_time)

    if from_dt and to_dt and from_dt >= to_dt:
        from_dt = None
        to_dt = None
        form.from_date.errors.append(msg_from)
        form.from_time.errors.append(msg_from)
        form.to_date.errors.append(msg_to)
        form.to_time.errors.append(msg_to)

    resource_ids = [r.id for r in form.resources.data]

    return render_template(
        "bookings/list.html", form=form, bookings=Booking
        .get_allowed_by_resource(from_dt, to_dt, resource_ids,
                                 form.filter_not_in_invoice.data))


@app.route("/bookings/", methods=["POST"])
@login_required()
def bookings_create():
    form = BookingFormCreate(request.form)

    if not form.validate():
        return render_template("bookings/new.html", form=form)

    start_dt = dt.combine(form.start_date.data, form.start_time.data)
    end_dt = dt.combine(form.end_date.data, form.end_time.data)

    if start_dt < dt.utcnow() and ADMIN not in current_user.roles():
        form.start_date.errors.append(msg_past)
        form.start_time.errors.append(msg_past)
        return render_template("bookings/new.html", form=form)

    if start_dt >= end_dt:
        form.start_date.errors.append(msg_start)
        form.start_time.errors.append(msg_start)
        form.end_date.errors.append(msg_end)
        form.end_time.errors.append(msg_end)
        return render_template("bookings/new.html", form=form)

    b = Booking(form.account.data.id, form.resource.data.id, start_dt, end_dt)

    if not Booking.is_free_time_slot(b):
        for field in [form.resource, form.start_date, form.start_time,
                      form.end_date, form.end_time]:
            field.errors.extend([msg_free_rts_1(form.resource.data),
                                 msg_free_rts_2])
        return render_template("bookings/new.html", form=form)

    db.session().add(b)
    db.session().commit()
    return redirect(url_for("bookings_single", booking_id=b.id))


@app.route("/bookings/<booking_id>/", methods=["GET"])
@login_required()
def bookings_single(booking_id):
    b = Booking.query.get(booking_id)

    if not b:
        return render_template("404.html", res_type="booking"), 404

    if b.id not in [b.id for b in Booking.get_allowed_by_account()]:
        return login_manager.unauthorized()

    return render_template("bookings/single.html", booking=b)


@app.route("/bookings/<booking_id>/update", methods=["GET"])
@login_required()
def bookings_form_update(booking_id):
    b = Booking.query.get(booking_id)

    if not b:
        return render_template("404.html", res_type="booking"), 404

    if ((b.start_dt <= dt.utcnow() and ADMIN not in current_user.roles())
       or b.id not in [b.id for b in Booking.get_allowed_by_account()]):
        return login_manager.unauthorized()

    form = BookingFormUpdate()
    form.account.data = b.account
    form.resource.data = b.resource
    form.start_date.data = b.start_dt.date()
    form.start_time.data = b.start_dt.time()
    form.end_date.data = b.end_dt.date()
    form.end_time.data = b.end_dt.time()
    return render_template("bookings/update.html", booking=b, form=form)


@app.route("/bookings/<booking_id>/", methods=["POST"])
@login_required()
def bookings_update(booking_id):
    b = Booking.query.get(booking_id)

    if not b:
        return render_template("404.html", res_type="booking"), 404

    if ((b.start_dt <= dt.utcnow() and ADMIN not in current_user.roles())
       or b.id not in [b.id for b in Booking.get_allowed_by_account()]):
        return login_manager.unauthorized()

    old_b = copy.deepcopy(b)
    form = BookingFormUpdate(request.form)

    if not form.validate():
        return render_template("bookings/update.html", booking=b, form=form)

    for field in [form.account, form.resource]:
        if field.data:
            setattr(b, field.name, field.data)

    b.start_dt = dt.combine(form.start_date.data, form.start_time.data)
    b.end_dt = dt.combine(form.end_date.data, form.end_time.data)

    if b.start_dt < dt.utcnow() and ADMIN not in current_user.roles():
        form.start_date.errors.append(msg_past)
        form.start_time.errors.append(msg_past)
        return render_template("bookings/update.html",
                               booking=old_b, form=form)

    if b.start_dt >= b.end_dt:
        for field in [form.start_date, form.start_time]:
            if field:
                field.errors.append(msg_start)
        for field in [form.end_date, form.end_time]:
            if field:
                field.errors.append(msg_end)
        return render_template("bookings/update.html",
                               booking=old_b, form=form)

    if not Booking.is_free_time_slot(b):
        for field in [form.resource, form.start_date, form.start_time,
                      form.end_date, form.end_time]:
            field.errors.extend([msg_free_rts_1(form.resource.data),
                                 msg_free_rts_2])
        return render_template("bookings/update.html",
                               booking=old_b, form=form)

    b.calculate_price()
    db.session().commit()
    return redirect(url_for("bookings_single", booking_id=b.id))


@app.route("/bookings/<booking_id>/delete", methods=["GET"])
@login_required()
def bookings_delete_ask(booking_id):
    b = Booking.query.get(booking_id)

    if not b:
        return render_template("404.html", res_type="booking"), 404

    if ((b.start_dt <= dt.utcnow() and ADMIN not in current_user.roles())
       or b.id not in [b.id for b in Booking.get_allowed_by_account()]):
        return login_manager.unauthorized()

    return render_template("bookings/delete.html", booking=b)


@app.route("/bookings/<booking_id>/delete", methods=["POST"])
@login_required()
def bookings_delete(booking_id):
    b = Booking.query.get(booking_id)

    if not b:
        return render_template("404.html", res_type="booking"), 404

    if ((b.start_dt <= dt.utcnow() and ADMIN not in current_user.roles())
       or b.id not in [b.id for b in Booking.get_allowed_by_account()]):
        return login_manager.unauthorized()

    db.session.delete(b)
    db.session.commit()
    return redirect(url_for("bookings_list"))
