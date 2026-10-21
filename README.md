# GrabSoMore eCommerce Application

A Django eCommerce web app where users register as vendors or buyers.

GitHub repository: https://github.com/valkyrie-dotcom/ecommerce-app

* **grabsomore**: registration, login, logout and password reset.
* **eCommerce**: stores, products, cart, checkout and reviews.

## Usage Features

* Vendors create, view, edit and remove stores, and add, view, edit and
  remove products in their stores.
* Buyers view products from different stores, add them to a cart kept in the
  session, and check out. A buyer cannot add more of a product than there is
  stock available.
* Checkout saves the order, reduces the stock, empties the cart and emails an
  invoice.
* Buyers leave reviews with a rating from 1 to 5. Reviews are verified if the
  buyer bought the product.
* Users confirm their password when registering, and each email address can
  only be used for one account.
* Users can reset forgotten passwords through an emailed link that expires
  after 5 minutes.
* A web API lets vendors create stores and add products, and lets buyers
  and vendors retrieve stores, products and reviews.
* A Reddit feed page shows posts from the r/django subreddit.

## Requirements

Install these before you start:

* Python 3.12 or later: https://www.python.org/downloads/
* Git: https://git-scm.com/downloads
* MariaDB: https://mariadb.org/download/ (remember the root password you
  choose during installation)

## Installation

The commands below are typed into a terminal:
* On Windows, use **Git Bash** (installed with Git).
* On Mac, use **Terminal**.

### 1. Clone the repository

```bash
git clone https://github.com/valkyrie-dotcom/ecommerce-app.git
```

### 2. Go into the project folder

```bash
cd ecommerce-app
```

All the commands from here on are run inside this folder.

### 3. Create a virtual environment inside the project folder

```bash
python -m venv venv
```

On Mac, use `python3` instead of `python` if `python` is not found.

### 4. Activate the virtual environment

* Windows (Git Bash):

  ```bash
  source venv/Scripts/activate
  ```

* Windows (Command Prompt):

  ```bat
  venv\Scripts\activate
  ```

* Mac or Linux:

  ```bash
  source venv/bin/activate
  ```

You will see `(venv)` at the start of the line once it is active. Activate
it again each time you open a new terminal.

### 5. Install the packages

```bash
pip install -r requirements.txt
```

### 6. Create the database in MariaDB

Open the MariaDB SQL terminal:
* On Windows, open **MySQL Client (MariaDB)**
from the Start menu, or open **Command Prompt (MariaDB)** from the Start menu
and type the command below.
* On Mac, type the command below in Terminal.

```bash
mysql -u root -p
```

Enter the root password you chose when installing MariaDB. The prompt changes
to `MariaDB [(none)]>`. Type these two lines, pressing Enter after each:

```sql
CREATE DATABASE ecommerce_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

### 7. Create the `.env` file

Copy the example file:

* Git Bash or Mac:

  ```bash
  cp .env.example .env
  ```

* Command Prompt:

  ```bat
  copy .env.example .env
  ```

Open `.env` in a text editor and set `DB_PASSWORD` to your MariaDB root
password. Leave the email lines commented out to have emails printed in the
terminal instead of sent.

### 8. Create the tables

```bash
python manage.py migrate
```

This also creates the **Vendors** and **Buyers** groups.

### 9. Create an admin user (optional)

```bash
python manage.py createsuperuser
```

## Running the project

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser. Press `Ctrl + C` in the
terminal to stop the server.

If no email details are set in `.env`, emails (invoices and password reset
links) are printed in the terminal.

## Web API

Test the API with Postman. Use **Basic Auth** with a registered username and
password, and send POST data as raw JSON.

| Method | Endpoint |
|--------|----------|
| GET | `/ecommerce/api/vendors/<vendor_id>/stores/` |
| GET | `/ecommerce/api/stores/<store_id>/products/` |
| GET | `/ecommerce/api/products/<product_id>/reviews/` |
| POST | `/ecommerce/api/stores/` |
| POST | `/ecommerce/api/products/` |

Example body for `POST /ecommerce/api/stores/` (the owner is your user ID):

```json
{"owner": 1, "name": "BaconShop", "description": "We sell Bacon!"}
```

Example body for `POST /ecommerce/api/products/`:

```json
{"store": 1, "name": "Bacon", "description": "Smoked", "price": "49.99", "stock": 10}
```

## Reddit feed

Open http://127.0.0.1:8000/ecommerce/reddit/ to see posts from r/django.

**Note:** the Reddit code follows the lesson, which fetches the public
`https://www.reddit.com/r/<subreddit>/.json` feed with only a User-Agent
header. Since May 2026 Reddit blocks these requests unless the user is
logged in, and returns `403 Forbidden`. When that happens, the terminal
prints "Failed to fetch data." and the page shows "Could not load posts from
Reddit." The code works again if Reddit allows the public feed.

## Project structure

```
ecommerce_app/
├── ecommerce_site/   # Project settings and URLs
├── grabsomore/       # Accounts app, base.html and the stylesheet
├── eCommerce/        # Shop app
├── Planning/         # Planning and diagrams
├── manage.py
├── requirements.txt
└── research_answers.md
```
