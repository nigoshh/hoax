## database structure

![database diagram](https://github.com/nigoshh/hoax/blob/master/documentation/db_diagram.png)

One thing that isn't immediately evident from the diagram is the relationship between invoice and booking; even though there is a junction table between them (invoice_booking), the relationship is still one-to-many. The junction table has been chosen to avoid using NULLs; a booking is always created before its invoice, so using NULLs would have been inevitable without the junction table. This one-to-many relationship has been marked structurally in the database schema (by defining a UNIQUE constraint for booking_id in invoice_booking) as well as in the SQLAlchemy model (by using the [single_parent](https://docs.sqlalchemy.org/en/latest/orm/relationship_api.html#sqlalchemy.orm.relationship.params.single_parent) keyword argument).

The SQLAlchemy [cascade](https://docs.sqlalchemy.org/en/latest/orm/cascades.html#unitofwork-cascades) keyword argument with value has been used in many relationships to facilitate records deletion; in these relationships, when a record is deleted, all records referencing it (via foreign key) are deleted automatically in the same session. Usually this has been adopted in the direction parent->children (one-to-many relationships), meaning that when a parent is deleted all its children are deleted automatically. Examples of this can be found in community->account, account->booking and resource->booking. In one case this construct has been used in the opposite direction (many-to-one), in the relationship booking->invoice. This follows the logic that if a booking is deleted, the invoice containing it isn't valid anymore (the total amount to be paid needs to be calculated again); so it makes sense to delete the invoice, which will also cause deletion of all the records in invoice_booking referencing it, meaning that all the bookings in the deleted invoice are "free" (orphan) once again, and can be put together to form a new invoice.

Some columns (other than the principal key) have been indexed to speed up the queries; these are mostly foreign key columns, and some other columns that can be used for filtering results, like account.username, invoice.paid or resource.type. Below you can find all CREATE TABLE and CREATE INDEX statements (all generated by SQLAlchemy).

```sql
CREATE TABLE community (
        id INTEGER NOT NULL,
        date_created DATETIME NOT NULL,
        date_modified DATETIME NOT NULL,
        address VARCHAR(144) NOT NULL,
        PRIMARY KEY (id),
        UNIQUE (address)
)

CREATE TABLE invoice (
        id INTEGER NOT NULL,
        date_created DATETIME NOT NULL,
        date_modified DATETIME NOT NULL,
        price NUMERIC NOT NULL CHECK (price >= 0),
        paid BOOLEAN NOT NULL,
        PRIMARY KEY (id),
        CHECK (paid IN (0, 1))
)

CREATE INDEX ix_invoice_paid ON invoice (paid)

CREATE TABLE account (
        id INTEGER NOT NULL,
        date_created DATETIME NOT NULL,
        date_modified DATETIME NOT NULL,
        community_id INTEGER NOT NULL,
        username VARCHAR(144) NOT NULL,
        pw_hash VARCHAR(512) NOT NULL,
        apartment VARCHAR(144) NOT NULL,
        forename VARCHAR(144) NOT NULL,
        surname VARCHAR(144) NOT NULL,
        email VARCHAR(144) NOT NULL,
        phone VARCHAR(144) NOT NULL,
        PRIMARY KEY (id),
        FOREIGN KEY(community_id) REFERENCES community (id)
)

CREATE UNIQUE INDEX ix_account_username ON account (username)
CREATE INDEX ix_account_community_id ON account (community_id)

CREATE TABLE admin (
        account_id INTEGER NOT NULL,
        community_id INTEGER NOT NULL,
        PRIMARY KEY (account_id, community_id),
        FOREIGN KEY(account_id) REFERENCES account (id),
        FOREIGN KEY(community_id) REFERENCES community (id)
)

CREATE INDEX ix_admin_community_id ON admin (community_id)
CREATE INDEX ix_admin_account_id ON admin (account_id)

CREATE TABLE resource (
        id INTEGER NOT NULL,
        date_created DATETIME NOT NULL,
        date_modified DATETIME NOT NULL,
        account_id INTEGER NOT NULL,
        address VARCHAR(144) NOT NULL,
        type VARCHAR(144) NOT NULL,
        name VARCHAR(144) NOT NULL,
        price NUMERIC NOT NULL CHECK (price >= 0 AND price <= 1000000),
        PRIMARY KEY (id),
        CONSTRAINT unique_atn UNIQUE (address, type, name),
        FOREIGN KEY(account_id) REFERENCES account (id)
)

CREATE INDEX ix_resource_type ON resource (type)
CREATE INDEX ix_resource_account_id ON resource (account_id)

CREATE TABLE community_resource (
        community_id INTEGER NOT NULL,
        resource_id INTEGER NOT NULL,
        PRIMARY KEY (community_id, resource_id),
        FOREIGN KEY(community_id) REFERENCES community (id),
        FOREIGN KEY(resource_id) REFERENCES resource (id)
)

CREATE INDEX ix_community_resource_resource_id ON community_resource (resource_id)
CREATE INDEX ix_community_resource_community_id ON community_resource (community_id)

CREATE TABLE booking (
        id INTEGER NOT NULL,
        date_created DATETIME NOT NULL,
        date_modified DATETIME NOT NULL,
        account_id INTEGER NOT NULL,
        resource_id INTEGER NOT NULL,
        start_dt DATETIME NOT NULL,
        end_dt DATETIME NOT NULL,
        price NUMERIC NOT NULL CHECK (price >= 0),
        PRIMARY KEY (id),
        CONSTRAINT time_direction CHECK (start_dt < end_dt),
        FOREIGN KEY(account_id) REFERENCES account (id),
        FOREIGN KEY(resource_id) REFERENCES resource (id)
)

CREATE INDEX ix_booking_start_dt ON booking (start_dt)
CREATE INDEX ix_booking_end_dt ON booking (end_dt)
CREATE INDEX ix_booking_resource_id ON booking (resource_id)
CREATE INDEX ix_booking_account_id ON booking (account_id)

CREATE TABLE invoice_booking (
        invoice_id INTEGER NOT NULL,
        booking_id INTEGER NOT NULL,
        PRIMARY KEY (invoice_id, booking_id),
        FOREIGN KEY(invoice_id) REFERENCES invoice (id),
        FOREIGN KEY(booking_id) REFERENCES booking (id)
)

CREATE UNIQUE INDEX ix_invoice_booking_booking_id ON invoice_booking (booking_id)
CREATE INDEX ix_invoice_booking_invoice_id ON invoice_booking (invoice_id)
```
