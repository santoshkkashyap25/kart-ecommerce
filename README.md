# KART - E-Commerce Platform

> A full-stack e-commerce platform built with Django, featuring 40+ features, security, and enterprise-grade architecture.

---

## Screenshots

<table>
  <tr>
    <td><img src="screenshots/home.jpg" alt="Homepage" width="400"/><br/><sub><b>Homepage</b></sub></td>
    <td><img src="screenshots/product.jpg" alt="Product Detail" width="400"/><br/><sub><b>Product Detail</b></sub></td>
    <td><img src="screenshots/filter.jpg" alt="Search & Filter" width="400"/><br/><sub><b>Search & Filter</b></sub></td>
  </tr>
</table>

---

## Key Features

### **Customer Experience**
- **Advanced Search** - Intelligent search with filters and sorting
- **Wishlist** - Save favorite products for later
- **Shopping Cart** - Real-time AJAX updates with persistent storage
- **Product Reviews** - 5-star rating system with verified purchase badges
- **Order Tracking** - Real-time status updates
- **Multiple Addresses** - Manage multiple shipping addresses seamlessly
- **Responsive Design** - Optimized for desktop, tablet, and mobile

### **Admin Dashboard**
- **Comprehensive Analytics** - Sales reports, revenue tracking, customer insights
- **Inventory Management** - Real-time stock tracking with low-stock alerts
- **Order Management** - Process orders, update status, generate invoices
- **Customer Management** - View history, lifetime value, segmentation
---

## Quick Start (Docker)

The fastest way to get KART running is using Docker. The setup is fully automated, including migrations and data seeding.

1.  **Clone and Configure**
    ```bash
    git clone https://github.com/santoshkkashyap25/kart.git
    cd kart
    cp .env.example .env
    ```

2.  **Start the Application**
    ```bash
    docker-compose up -d --build
    ```
    This command builds the image and starts the server. It also automatically runs migrations, seeds the database with dummy products, and creates an admin account.

3.  **Access the Store**
    - Storefront: [http://localhost:8000](http://localhost:8000)
    - Admin Panel: [http://localhost:8000/admin](http://localhost:8000/admin) (User: `admin`, Pass: `adminpass`)

---

### Manual Installation (Local)

If you prefer to run it without Docker:
```bash
# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and seed data
python manage.py migrate
python manage.py seed_data

# Create superuser and run
python manage.py createsuperuser
python manage.py runserver
```

---
## Testing

The project includes a robust test suite covering models, views, and forms.

```bash
# Run all tests (inside Docker)
docker-compose exec web python manage.py test

# Run specific suites (Local)
python manage.py test app.tests.test_models
python manage.py test app.tests.test_views
```
