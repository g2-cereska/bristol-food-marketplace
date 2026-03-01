# Bristol Regional Food Network – Digital Marketplace (Sprint 1)

## Context

Initial backend scaffold for a multi-producer marketplace (producers list products; customers place orders).
Based on the case study requirements for product listings, browsing, and order handling. :contentReference[oaicite:0]{index=0}

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

## How to run locally

```bash
python -m venv .venv
# activate venv...
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 
```

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

## Sprint 2 plan

- Authentication + roles
- Filtering/search for products + categories
- Inventory rules (availability windows)
- Start modelling multi-vendor order splitting / commission

## Team & Contribution Note

Initial attempts were made to coordinate Sprint 1 work with assigned group members. 
At the time of submission, no confirmed collaborative contributions were received.

To avoid missing the sprint deadline, the current implementation was developed independently. 
If group collaboration resumes, contributions will be tracked via version control.
