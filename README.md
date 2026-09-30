# Radhakrishna Communication & Electronics — e-commerce catalogue

A responsive Flask website converted from the original Streamlit catalogue. It includes a SQLite product database, public product catalogue, search/category filtering, product detail pages, image gallery with hover zoom and enlarged image modal, WhatsApp enquiry/order links, and an admin dashboard for creating/editing/hiding/deleting products.

## Requirements
- Python 3.10+
- pip

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Set environment variables before starting (recommended):

```bash
export SECRET_KEY='use-a-long-random-secret-value'
export ADMIN_USERNAME='your-admin-name'
export ADMIN_PASSWORD='use-a-unique-password-at-least-12-characters'
export WHATSAPP_NUMBER='91XXXXXXXXXX'
python app.py
```

On Windows PowerShell, use `$env:SECRET_KEY='...'` etc. Then open http://127.0.0.1:5000.

**First run defaults (development only):** username `admin`, password `ChangeMe123!`. Set `ADMIN_USERNAME` and `ADMIN_PASSWORD` before the first run in any real deployment. The initial admin account is created only when the database has no admin records. Once running, visit `/admin/password` to change the password. If you already initialized the database with defaults, change the password after login.

## WhatsApp setup
Set `WHATSAPP_NUMBER` to your store's WhatsApp number including country code, digits only (no `+`, spaces, or hyphens). The current default is a placeholder. The order button opens WhatsApp with a pre-filled message; customers still need to send the message to submit their enquiry/order. This is not a payment gateway or automated order-management system.

## Admin product management
Visit `/admin`, sign in, and add/edit/delete products. For images, paste publicly accessible HTTPS image URLs. Gallery URLs should be separated by commas. Untick “Show this product” to hide an item without deleting it.

## Database
SQLite database file `shop.db` is created automatically and seeded with the four sample products on first run. Back up this file regularly. For production, use a persistent disk/volume and set `DATABASE_PATH` accordingly. SQLite is appropriate for a small catalogue; for high traffic or multiple app instances, migrate to PostgreSQL.

## Production notes
- Do not use the development server for production. Run behind a production WSGI server (for example, Waitress on Windows or Gunicorn on Linux) and HTTPS.
- Set a strong, private `SECRET_KEY`, a unique admin password, and your real WhatsApp number.
- Keep the database on persistent storage and back it up.
- This starter does not include payment processing, customer accounts, inventory reservations, order records, tax/shipping calculations, image uploads, or CSRF protection. Add these before using it as a full transactional online shop. Admin actions should be protected with CSRF tokens and rate limiting before public deployment.
