# HOAX booking

[heroku app](https://hoax-booking.herokuapp.com/)

[user stories](https://github.com/nigoshh/hoax/blob/master/documentation/user_stories.md)

[database diagram](https://github.com/nigoshh/hoax/blob/master/documentation/db_diagram.png)

[original description (in Finnish)](https://advancedkittenry.github.io/suunnittelu_ja_tyoymparisto/aiheet/Taloyhtion_palvelut.html)

The objective is to build a booking system for HOAX student housing's shared resources, like saunas, laundry rooms and common rooms. Each housing complex has its own resources, which can be booked and used by all the tenants. The landlord entrusts one or more admins to manage one or more housing complex; the admins can add and remove resources, and decide at what times they can be booked. Reservations can be single or recurring. Single reservations can be made two weeks ahead at the earliest, and they can be canceled up to one day before their starting time. Recurring reservations can be canceled at any time. Each resource has a fixed unit length (like one hour) with a given price. Only the tenant who made the reservation has access to the resource at that given time; for this purpose a personal code has to be entered at the door.

Reservations automatically get a reference number in increasing order. Tenants can compose an invoice to pay for many single reservations at once; the invoice's reference number will be the last reservation's reference number. The admins will use this reference number to mark the invoice as payed. If a tenant doesn't order an invoice after a given amount of time, an admin will generate one. Recurring reservations are payed together with the rent. Admins can see a summary of resource use and payments.

Some functionalities:
- login
- create and cancel reservations
- compose invoices
- summary of resource use
- summary of payments
- password change

University of Helsinki, Database Application course project (tsoha)
