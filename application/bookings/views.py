import copy
from datetime import datetime as dt
from application import app, db
from flask import redirect, render_template, request, url_for
from flask_login import login_required
from application.bookings.models import Booking
from application.bookings.forms import BookingFormCreate, BookingFormUpdate


def msg_free_rts_1(resource):
    return ("Resource %s %s %d is already booked in this time slot."
            % (resource.address, resource.type, resource.number))


msg_free_rts_2 = "Please check the bookings' list to find a free time slot."
msg_end = "Ending time must be after starting time."
msg_start = "Starting time must be before ending time."


@app.route("/bookings/new/")
@login_required
def bookings_form_create():
    form = BookingFormCreate()
    return render_template("bookings/new.html", form=form)


@app.route("/bookings/", methods=["GET"])
def bookings_list():
    return render_template("bookings/list.html",
                           bookings=Booking.query.order_by("start_dt"))


@app.route("/bookings/", methods=["POST"])
@login_required
def bookings_create():
    form = BookingFormCreate(request.form)

    if not form.validate():
        return render_template("bookings/new.html", form=form)

    start_dt = dt.combine(form.start_date.data, form.start_time.data)
    end_dt = dt.combine(form.end_date.data, form.end_time.data)

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

    b.calculate_price()
    db.session().add(b)
    db.session().commit()
    return redirect(url_for("bookings_single", booking_id=b.id))


@app.route("/bookings/<booking_id>/", methods=["GET"])
@login_required
def bookings_single(booking_id):
    b = Booking.query.get(booking_id)
    return render_template("bookings/single.html", booking=b)


@app.route("/bookings/<booking_id>/update", methods=["GET"])
@login_required
def bookings_form_update(booking_id):
    b = Booking.query.get(booking_id)
    form = BookingFormUpdate()
    form.account.data = b.account
    form.resource.data = b.resource
    form.start_date.data = b.start_dt.date()
    form.start_time.data = b.start_dt.time()
    form.end_date.data = b.end_dt.date()
    form.end_time.data = b.end_dt.time()
    return render_template("bookings/update.html", booking=b, form=form)


@app.route("/bookings/<booking_id>/", methods=["POST"])
@login_required
def bookings_update(booking_id):
    b = Booking.query.get(booking_id)
    old_b = copy.deepcopy(b)
    form = BookingFormUpdate(request.form)

    if not form.validate():
        return render_template("bookings/update.html", booking=b, form=form)

    for field in [form.account, form.resource]:
        if field.data:
            setattr(b, field.name, field.data)

    b.start_dt = dt.combine(form.start_date.data, form.start_time.data)
    b.end_dt = dt.combine(form.end_date.data, form.end_time.data)

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
@login_required
def bookings_delete_ask(booking_id):
    b = Booking.query.get(booking_id)
    return render_template("bookings/delete.html", booking=b)


@app.route("/bookings/<booking_id>/delete", methods=["POST"])
@login_required
def bookings_delete(booking_id):
    b = Booking.query.get(booking_id)
    db.session.delete(b)
    db.session.commit()
    return redirect(url_for("bookings_list"))
