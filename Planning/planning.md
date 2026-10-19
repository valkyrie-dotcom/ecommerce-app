# Planning: Grabsomore eCommerce Application

## 1. Requirements

Users should be able to register and log in as either:

1. Vendors
- create, view, edit and remove stores
- add, view, edit and remove products in their stores

2. Buyers
- view products from different stores
- add products to a cart that is kept in the session
- only add as many of a product as there is stock available
- check out, which empties the cart, saves the order, reduces the stock and
  emails an invoice
- leave reviews with a rating from 1 to 5 (verified if buyer has bought
  product, unverified if not)

On registration, users confirm their password, and each email address can
only be used for one account.

Users should be able to reset forgotten password as below:
- request password reset link
- provide email adress to be reset
- if email exists, a reset link is sent to said email adress
- the link contains a token that expires after 5 minutes
- the user can open the link from their email to reset their password
- the user can log in normally with the new password thereafter

The database will be MariaDB (as I have not worked with this before and
would like to gain the experience). The tables will be created via migrations

## 2. Design

The design diagrams can be found in 'Planning/diagrams':

- `use_case_diagram`: what buyers and vendors can do
- `class_diagram`: the models and how they relate
- `sequence_authentication`: logging in and permission checks
- `sequence_purchase`: cart, checkout and reviews
- `sequence_password_reset`: requesting and using a reset link

## 3. User interface

Every page extends `base.html`, which loads the shared stylesheet and shows a
navigation bar at the top, plus any success or error messages. The Cart link
only shows for buyers, and the My Stores link only shows for vendors.

- **Login and Register:** simple forms. Register as a buyer or vendor, and
  confirm the password.
- **Welcome:** a Go to Store button and a Manage My Stores button for vendors.
  Logout is in the navigation bar.
- **Product Catalog:** all products with their store, description, price and
  stock. Buyers see an Add button, or "Out of stock" when there is none left.
- **Product Page:** search for a product by name to see its details and
  reviews (with their rating, marked verified or unverified). Buyers can leave
  a review with a rating from 1 to 5 here.
  Product pages should also be reachable by clicking on the product name,
  which will contain a link that reroutes to the product page.
- **My Stores (vendors):** each store with its products, and buttons to create,
  edit and remove stores and products.
- **Cart (buyers):** items, subtotals, total, and Checkout and Clear Cart
  buttons.
- **Order Complete:** the invoice and a note that it was emailed.
- **Password reset pages:** request form, email sent, new password form, and
  expired or invalid link pages.

## 4. Access control and data security

- Every shop page needs the user to be logged in (`login_required`).
  Anyone not logged in is sent to the login page.
- On registration the user is added to the **Vendors** or **Buyers** group.
  The groups and their permissions are created when migrations run.
  - Vendors: add, change, delete and view stores and products.
  - Buyers: view products, add orders and add reviews.
- Each view checks the permission with `has_perm` and shows an error if the
  user does not have it.
- Vendors can only edit or remove their own stores and products.
- Passwords are hashed by Django. They must not be empty and must pass
  Django's built-in password validators (at least 8 characters, not too
  similar to the username, not a common password and not all numbers).
- Reset tokens are stored hashed, expire after 5 minutes and are deleted once
  used.
- The reset page shows the same message whether or not the email exists.
- Forms use CSRF tokens.
- The secret key and the database and email passwords are kept in a `.env`
  file that is not committed.

## 5. Failure handling

| What goes wrong | What happens |
|-----------------|--------------|
| User is not logged in | Redirected to the login page |
| User does not have permission | The page shows an error message |
| Vendor opens another vendor's store or product | 404 page |
| Wrong username or password | Login page shows "Invalid credentials" |
| Username empty or already taken, or password empty or too weak | Register page shows the error |
| Passwords do not match on registration | Register page shows "Passwords do not match." |
| Email address already used by another account | Register page shows the error |
| Reset password empty, too weak or not matching | Reset page shows the error |
| Reset link expired | Expired page with a link to request a new one |
| Reset link invalid or already used | Invalid page with a link to request a new one |
| Product name not found when searching | Product page shows "Product not found." |
| Invalid form input | The form is shown again with the errors |
| Checkout with an empty cart | Back to the cart page |
| Review without a rating from 1 to 5 or without a comment | Product page shows the error |
| Adding more to the cart than the stock available | Cart page shows how many are in stock |
| Stock dropped below the cart quantity before checkout | Cart page shows the error and no order is saved |
| Invoice email cannot be sent | Order is still saved and a message says the email failed |
