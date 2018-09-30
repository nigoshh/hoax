## user stories

- as a tenant, I can book my housing community's common resources, like saunas and laundry rooms
- as a tenant, I can make single or recurring reservations for my housing community's common resources
- as a tenant, I can cancel a single reservation I made, provided that I do that at least one day before its starting time
- as a tenant, I can access the resource I reserved by entering my personal code at the door
- as a tenant, I can manage my user account and update my personal information like email address and password
- as a tenant, I can compose an invoice to pay for the single reservations I made

- as an admin, I can assign admins to manage housing communities
- as an admin, I can specify what common resources can be booked, and at what times they can be booked
- as an admin, I can create/delete a user account, for example when a tenant moves in/out
- as an admin, I can compose invoices for tenants
- as an admin, I can see a summary of resource use and payments

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
