# HOAX booking

[heroku app](https://hoax-booking.herokuapp.com/)

[database structure](https://github.com/nigoshh/hoax/blob/master/documentation/db_structure.md)

[user stories and SQL queries](https://github.com/nigoshh/hoax/blob/master/documentation/user_stories.md)

[original description (in Finnish)](https://advancedkittenry.github.io/suunnittelu_ja_tyoymparisto/aiheet/Taloyhtion_palvelut.html)

[installation](#installation)

[user guide](#user-guide)

## description

The objective is to build a booking system for HOAX student housing's shared resources, like saunas, laundry rooms and common rooms. Each housing community has access to certain resources, which can be booked and used by all the members of the community (usually, the tenants living at the community's address). An admin can manage one or more housing communities. Regular users can share a resource with one or more communities, and they can book the resources to which their community has access. Each resource has a given price per hour. Only the tenant whose name is on the reservation has access to the resource at that given time; for this purpose she can enter her password at the door.

Both regular users and admins can compose an invoice to pay for one or many reservations. The admins can use the invoice's reference number to find it and mark it as paid. If a tenant doesn't compose an invoice after a given amount of time, an admin will compose one.

Some functionalities:
- login
- create and cancel reservations
- compose invoices
- password change

University of Helsinki, Database Application course project (tsoha)

## installation

### local

To run the app locally, first install [Python](https://www.python.org/downloads/), then create and activate a virtual environment as explained [here](https://docs.python.org/3/library/venv.html#creating-virtual-environments) (commands vary depending on your OS). Then install dependencies by running

```shell
pip install -r requirements.txt
```

To execute the code run

```shell
python3 run.py
```

or alternatively (on Windows, with Python in your PATH)

```shell
python run.py
```

### Heroku

The app doesn't require additional configuration to be deployed on Heroku. Deploy either [with Git](https://devcenter.heroku.com/articles/git#for-a-new-heroku-app) or [directly from Github](https://devcenter.heroku.com/articles/github-integration). Then add the [Postgres add-on](https://elements.heroku.com/addons/heroku-postgresql), using either the [command line interface](https://devcenter.heroku.com/articles/managing-add-ons#creating-an-add-on) or the [dashboard](https://devcenter.heroku.com/articles/managing-add-ons#add-an-add-on).

## user guide

If nothing exists in the app, first you have to create a community. Then you can create an account (with admin privileges, if you want). Then you can log in, and create a resource. Then you can book that resource. Then you can create an invoice, that includes a user's bookings.
