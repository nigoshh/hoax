# HOAX booking

[heroku app](https://hoax-booking.herokuapp.com/)

[database structure](https://github.com/nigoshh/hoax/blob/master/documentation/db_structure.md)

[user stories and SQL queries](https://github.com/nigoshh/hoax/blob/master/documentation/user_stories.md)

[original description (in Finnish)](https://advancedkittenry.github.io/suunnittelu_ja_tyoymparisto/aiheet/Taloyhtion_palvelut.html)

The objective is to build a booking system for HOAX student housing's shared resources, like saunas, laundry rooms and common rooms. Each housing community has its own resources, which can be booked and used by all the tenants. The head of HOAX entrusts one or more admins to manage one or more housing communities; the admins can add and remove resources, and decide at what times they can be booked. Reservations can be single or recurring. Single reservations can be made two weeks ahead at the earliest, and they can be canceled up to one day before their starting time. Recurring reservations can be canceled at any time. Each resource has a given price per hour. Only the tenant whose name is on the reservation has access to the resource at that given time; for this purpose she can enter her password at the door.

Tenants can compose an invoice to pay for many single reservations at once. The admins will use the invoice's reference number to find it and mark it as paid. If a tenant doesn't compose an invoice after a given amount of time, an admin will compose one. Recurring reservations are paid together with the rent. Admins can see a summary of resource use and payments.

Some functionalities:
- login
- create and cancel reservations
- compose invoices
- summary of resource use
- summary of payments
- password change

University of Helsinki, Database Application course project (tsoha)
