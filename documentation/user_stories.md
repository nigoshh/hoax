## user stories

- as a user, I can see lists of communities and resources
- as a registered user, I can share a resource I own (or have access to) with one or many communities
- as a registered user, I can book the resources that my community has access to, like saunas, laundry rooms, or whatever other users have decided to share (like a piano)
- as a registered user, I can access the resource I reserved by entering my password at the door
- as a registered user, I can manage my user account and update my personal information like email address and password
- as a registered user, I can compose an invoice to pay for the reservations I made

- as an admin, I can manage one or more housing communities
- as an admin, I can delete a user account
- as an admin, I can see lists and details of accounts, bookings and invoices related to the communities I manage
- as an admin, I can compose invoices for regular users

## textual SQL queries

This textual SQL query can be found in [accounts/models.py](https://github.com/nigoshh/hoax/blob/master/application/accounts/models.py); it's used in the forms in [booking/forms.py](https://github.com/nigoshh/hoax/blob/master/application/bookings/forms.py) to make a list of accounts that can be selected as liable for the booking, using the [current_user](https://flask-login.readthedocs.io/en/latest/#flask_login.current_user)'s id (parameter :user_id in the query's [prepared statement](https://en.wikipedia.org/wiki/Prepared_statement)). The logic is that if the logged in user (current_user) isn't an admin, she can choose only herself as the account liable for the booking; if she is an admin, she can choose the liable account also from all the accounts in the communities that she administers.

```sql
SELECT * FROM account
    WHERE community_id IN
        (SELECT community.id FROM community
            INNER JOIN admin ON community.id = admin.community_id
            WHERE admin.account_id = :user_id)
    OR id = :user_id
```

This textual SQL query can be found in [resources/models.py](https://github.com/nigoshh/hoax/blob/master/application/resources/models.py); in a similar manner as the previous one, it's used in the forms in [booking/forms.py](https://github.com/nigoshh/hoax/blob/master/application/bookings/forms.py) to make a list of all the resources that can be booked by the logged in user (current_user). The logic is that if the logged is user isn't an admin, she can only book resources that are accessible by the community she is part of; if she is an admin, she can also book resources that are accessible by all the communities that she administers.

```sql
SELECT * FROM resource
    WHERE id IN
        (SELECT DISTINCT resource_id FROM community_resource, admin
            WHERE community_resource.community_id = admin.community_id
            AND admin.account_id = 1)
    OR id IN
        (SELECT DISTINCT resource_id FROM community_resource, account
            WHERE community_resource.community_id = account.community_id
            AND account.id = 1)
```

The following textual SQL query can be found in [invoices/models.py](https://github.com/nigoshh/hoax/blob/master/application/invoices/models.py). It's used to make a list of all the unpaid invoices that a user can see, depending on her user role.

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
    AND paid = 0
    ORDER BY date_created
```
