# Bristol Regional Food Network – Digital Marketplace (Sprint 1)

## Context

Initial backend scaffold for a multi-producer marketplace (producers list products; customers place orders).
Based on the case study requirements for product listings, browsing, and order handling.

## Sprint 1 Goal

Deliver a working Django REST API foundation: core models + CRUD endpoints + admin for data entry.

## What’s Implemented

- Django REST API with `Producer`, `Product`, and `Order` models
- Role-based permissions:
  - Staff/Admin users can create/update/delete producers and products
  - Authenticated customers can browse catalogue and create orders
  - Anonymous users can browse (read-only)
- Session-based authentication (Django REST browsable API login)
- Search filtering on products (name and description)
- Optimised querysets using `select_related` and `prefetch_related`
- Docker support (Dockerfile + docker-compose)
- SQLite database with local persistence

## Running the Project Locally

1. Clone the repository:

git clone <repository-url>
cd bristol-food-marketplace

2. Create a virtual environment:

python -m venv .venv

3. Activate the environment

Windows:
.venv\Scripts\activate

Mac/Linux:
source .venv/bin/activate

4. Install dependencies:

pip install -r requirements.txt

5. Apply database migrations:

python manage.py migrate

6. Run the development server:

python manage.py runserver

The API will be available at:

http://127.0.0.1:8000/api/

## Running with Docker

If Docker Desktop is installed, the project can be started using:

docker compose up --build

The application will then be available at:

http://localhost:8000/api/

## Logging into the API

The Django REST browsable API supports login via:

http://127.0.0.1:8000/api-auth/login/

Log in using a Django user account.

Staff/Admin users will be able to create producers and products.
Regular users can browse products and create orders.

## API Endpoints & Permissions

### Producers
- `GET /api/producers/` → Public read access
- `POST /api/producers/` → Staff only

### Products
- `GET /api/products/` → Public read access
- `POST /api/products/` → Staff only
- Search supported via `?search=keyword`

### Orders
- `GET /api/orders/` → Authenticated users
- `POST /api/orders/` → Authenticated users

## How to Verify Permissions

1. Log in as a staff user:
   - POST form is visible on `/api/products/` and `/api/producers/`

2. Log in as a customer:
   - No POST form appears for producers or products
   - Order creation form is visible

3. Log out:
   - Catalogue remains viewable (read-only)

## Known Limitations

- Order ownership is not restricted per user (all authenticated users can view orders)
- No pagination implemented
- SQLite used instead of production-grade database
- No automated tests implemented yet
- API versioning not yet introduced

## Sprint 2 Plan

- Improve order ownership (users should only see their own orders)
- Add pagination for product listings
- Introduce API versioning
- Implement product categories and improved filtering
- Begin modelling multi-vendor order splitting / commission logic

