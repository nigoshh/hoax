## database structure

![database diagram](https://github.com/nigoshh/hoax/blob/master/documentation/db_diagram.png)

One thing that isn't immediately evident from the diagram is the relationship between invoice and booking; even though there is a junction table between them (invoice_booking), the relationship is still one-to-many. The junction table has been chosen to avoid using NULLs; a booking is always created before its invoice, so using NULLs would have been inevitable without the junction table. This one-to-many relationship has been marked structurally in the database schema (by defining a UNIQUE constraint for booking_id in invoice_booking) as well as in the SQLAlchemy model (by using the [single_parent](https://docs.sqlalchemy.org/en/latest/orm/relationship_api.html#sqlalchemy.orm.relationship.params.single_parent) keyword argument).

The SQLAlchemy [cascade](https://docs.sqlalchemy.org/en/latest/orm/cascades.html#unitofwork-cascades) keyword argument with value has been used in many relationships to facilitate records deletion; in these relationships, when a record is deleted, all records referencing it (via foreign key) are deleted automatically in the same session. Usually this has been adopted in the direction parent->children (one-to-many relationships), meaning that when a parent is deleted all its children are deleted automatically. Examples of this can be found in community->account, account->booking and resource->booking. In one case this construct has been used in the opposite direction (many-to-one), in the relationship booking->invoice. This follows the logic that if a booking is deleted, the invoice containing it isn't valid anymore (the total amount to be payed needs to be calculated again); so it makes sense to delete the invoice, which will also cause deletion of all the records in invoice_booking referencing it, meaning that all the bookings in the deleted invoice are "free" (orphan) once again, and can be put together to form a new invoice.