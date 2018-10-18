## user stories

- as a user, I can see lists of communities and resources
- as a user, the list of communities I see includes stats about how many members are there in each community, and how many resources they have access to
- as a user, I can see details about a community, including the specific resources its members have access to
- as a user, I can see details about a resource, including the communities whose members are allowed access to that resource, and the resource's price

- as a registered user, I can share a resource I own (or have access to) with one or many communities
- as a registered user, I can book the resources that my community has access to, like saunas, laundry rooms, or whatever other users have decided to share (like a piano)
- as a registered user, I can access the resource I reserved by entering my password at the door
- as a registered user, I can manage my user account and update my personal information like email address and password
- as a registered user, I can compose an invoice to pay for the reservations I made

- as an admin, I can manage one or more housing communities
- as an admin, I can delete a user account
- as an admin, I can see lists and details of accounts, bookings and invoices related to the communities I manage
- as an admin, the list of accounts I can see includes each account's debt
- as an admin, I can see details about each community I administer, including which accounts are its members and which accounts are its admins
- as an admin, I can compose invoices for regular users

## textual SQL queries

### aggregate queries

The following aggregate query can be found in [accounts/models.py](https://github.com/nigoshh/hoax/blob/master/application/accounts/models.py); it's used in [accounts/views.py](https://github.com/nigoshh/hoax/blob/master/application/accounts/views.py) in the function _account_list_ to make a list of accounts for the logged in admin. The list includes only the accounts that are from the communities administered by the logged in admin (plus the admin's own account); a similar logic is used in many other textual queries shown below. This is achieved using the [current_user](https://flask-login.readthedocs.io/en/latest/#flask_login.current_user)'s id (parameter :user_id in the query's [prepared statement](https://en.wikipedia.org/wiki/Prepared_statement)). The aggregate function in the query is _SUM_, which calculates the total debt for each account. A booking's price is included into the debt only if the booking isn't in any invoice, or if the invoiced hasn't been paid yet; also, bookings which have not started yet (and thus could be canceled) are not included. Boolean _TRUE_ is given as a parameter to allow compatibility between SQLite and PostgreSQL (they have different data type representations for Boolean values). _IS NOT TRUE_ includes _NULL_ values resulting from the _LEFT JOIN_. The query's rows are ordered first by _debt_ (accounts with bigger debt first), and then by _account.date_created_, with the logic that if a newer account has already a big debt, it's probably a good idea to keep an eye on it.

```sql
SELECT account.id, account.username,
account.apartment, community.address,
COALESCE(debt.debt, 0) AS account_debt
    FROM community LEFT JOIN admin
        ON admin.community_id = community.id
    INNER JOIN account
        ON account.community_id = community.id
    LEFT JOIN
        (SELECT booking.account_id, SUM(booking.price) AS debt
            FROM booking
            LEFT JOIN invoice_booking
                ON invoice_booking.booking_id = booking.id
            LEFT JOIN invoice
                ON invoice.id = invoice_booking.invoice_id
            WHERE booking.start_dt <= :current_dt
            AND invoice.paid IS NOT :true
            GROUP BY booking.account_id
        ) AS debt 
        ON debt.account_id = account.id
    WHERE admin.account_id = :user_id
    OR account.id = :user_id
    ORDER BY account_debt DESC, account.date_created DESC
```

The following textual SQL query can be found in [communities/models.py](https://github.com/nigoshh/hoax/blob/master/application/communities/models.py). It's used in [communities/views.py](https://github.com/nigoshh/hoax/blob/master/application/communities/views.py) to get a list of all queries, including some stats. The stats are the number of accounts which are members of a community, and the number of resources a community has access to; both are obtained using the aggregate function _COUNT_. The list's order is somehow arbitrary (meaning that it could very well be another one); it's logic is that an unregistered user is probably more interested in communities that have access to many resources.

```sql
SELECT community.id, community.address,
COUNT(DISTINCT account.id) AS accounts,
COUNT(DISTINCT community_resource.resource_id) AS resources
    FROM community
    LEFT JOIN account
        ON account.community_id = community.id
    LEFT JOIN community_resource
        ON community_resource.community_id = community.id
    GROUP BY community.id
    ORDER BY resources DESC, accounts DESC, community.address
```

### other textual queries

The following textual SQL query can be found in [accounts/models.py](https://github.com/nigoshh/hoax/blob/master/application/accounts/models.py); it's used in the forms in [booking/forms.py](https://github.com/nigoshh/hoax/blob/master/application/bookings/forms.py) to make a list of accounts that can be selected as liable for the booking. The logic is that if the logged in user (_current_user_) isn't an admin, she can choose only herself as the account liable for the booking; if she is an admin, she can choose the liable account also from all the accounts in the communities that she administers.

```sql
SELECT * FROM account
    WHERE community_id IN
        (SELECT community.id FROM community
            INNER JOIN admin ON community.id = admin.community_id
            WHERE admin.account_id = :user_id)
    OR id = :user_id
```

The following textual SQL query can be found in [bookings/models.py](https://github.com/nigoshh/hoax/blob/master/application/bookings/models.py). It's used to check that a time slot is free, when creating a new booking, or updating an existing one. The last row is added only when updating an existing booking. The _:booking_id_ parameter is the booking's id, so that it can be excluded from the query; this is because when updating a booking, the time slot occupied by it should be considered free to use.

```sql
SELECT id FROM booking
    WHERE resource_id = :resource_id
    AND end_dt > :start_dt
    AND start_dt < :end_dt
    AND id <> :booking_id
```

The following textual SQL query can be found in [bookings/models.py](https://github.com/nigoshh/hoax/blob/master/application/bookings/models.py); it's used in the forms in [invoices/forms.py](https://github.com/nigoshh/hoax/blob/master/application/invoices/forms.py) to make a list of all the bookings accessible by a user, depending on her user role. Only the bookings which are not yet in an invoice are displayed. The third to last row is included only when updating an existing invoice, so that the bookings in it are included into the list.

```sql
SELECT * FROM booking
    WHERE (account_id IN
        (SELECT account.id FROM account
            INNER JOIN admin
                ON account.community_id = admin.community_id
            WHERE admin.account_id = :user_id)
        OR account_id = :user_id)
    AND id NOT IN
        (SELECT booking_id FROM invoice_booking
            WHERE invoice_id <> :invoice_id
        )
    ORDER BY start_dt
```

The following textual SQL query can be found in [communities/models.py](https://github.com/nigoshh/hoax/blob/master/application/communities/models.py). It's used in [communities/views.py](https://github.com/nigoshh/hoax/blob/master/application/communities/views.py) in many routes to authorize admin access to a community only if they administer that given community.

```sql
SELECT * FROM community
    WHERE id IN
        (SELECT community.id FROM community
            INNER JOIN admin
                ON community.id = admin.community_id
            WHERE admin.account_id = :user_id)
    ORDER BY address
```

The following textual SQL query can be found in [invoices/models.py](https://github.com/nigoshh/hoax/blob/master/application/invoices/models.py). It's used to make a list of all the unpaid invoices accessible by a user, depending on her user role. The second to last row can be omitted; in that case all invoices are displayed (also those that have already been paid). Boolean _FALSE_ is given as a parameter to allow compatibility between SQLite and PostgreSQL.

```sql
SELECT * FROM invoice
    WHERE id IN
        (SELECT invoice_id FROM invoice_booking
            INNER JOIN booking
            ON invoice_booking.booking_id = booking.id
            WHERE booking.account_id IN
                (SELECT id FROM account
                    WHERE community_id IN
                        (SELECT community.id FROM community
                            INNER JOIN admin
                            ON community.id = admin.community_id
                            WHERE admin.account_id = :user_id)
                    OR id = :user_id))
    AND paid IS :false
    ORDER BY date_created
```

The following textual SQL query can be found in [resources/models.py](https://github.com/nigoshh/hoax/blob/master/application/resources/models.py). It's a really basic query, but it was quicker to write it in plain SQL than it would have been to figure out how to write it with SQLAlchemy's [order_by](https://docs.sqlalchemy.org/en/latest/orm/query.html?highlight=order_by#sqlalchemy.orm.query.Query.order_by).

```sql
SELECT * FROM resource
ORDER BY address, type, name
```

The following textual SQL query can be found in [resources/models.py](https://github.com/nigoshh/hoax/blob/master/application/resources/models.py); it's used in the forms in [booking/forms.py](https://github.com/nigoshh/hoax/blob/master/application/bookings/forms.py) to make a list of all the resources that can be booked by the logged in user (_current_user_). The logic is that if the logged is user isn't an admin, she can only book resources that are accessible by the community she is part of; if she is an admin, she can also book resources that are accessible by all the communities that she administers.

```sql
SELECT * FROM resource
    WHERE id IN
        (SELECT DISTINCT resource_id FROM community_resource, admin
            WHERE community_resource.community_id = admin.community_id
            AND admin.account_id = :user_id)
    OR id IN
        (SELECT DISTINCT resource_id FROM community_resource, account
            WHERE community_resource.community_id = account.community_id
            AND account.id = :user_id)
```
