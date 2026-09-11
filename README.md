# KART — E-Commerce Web Application

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.0-7952B3?style=flat-square&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-46E3B7?style=flat-square&logo=render&logoColor=white)](https://kart-pcn0.onrender.com/)

> 🚀 **Live Demo:** [https://kart-pcn0.onrender.com/](https://kart-pcn0.onrender.com/)  
> 🛒 **Wishlist:** [https://kart-pcn0.onrender.com/wishlist/](https://kart-pcn0.onrender.com/wishlist/)

A full-stack monolithic e-commerce application built with **Python** and **Django** using the Model-View-Template (MVT) pattern. It covers the complete retail journey: product catalog, search & filtering, real-time AJAX cart, wishlist, multi-address checkout, order lifecycle tracking, customer reviews, and a customized Django administration panel.

---

## Table of Contents

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Architecture](#project-architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Installation (venv)](#local-installation-venv)
  - [Docker Installation](#docker-installation)
- [Environment Configuration](#environment-configuration)
- [Automated Tests](#automated-tests)

---

## Overview

KART was developed as a personal project to build a clean, resilient, and fully functional online storefront from scratch. It avoids heavy third-party e-commerce packages, implementing core functionality natively through Django models, views, custom management commands, and Bootstrap frontend templates with lightweight AJAX interactions.

---

## Screenshots

<table>
  <tr>
    <td align="center"><b>Storefront Homepage</b></td>
    <td align="center"><b>Product Detail & Reviews</b></td>
  </tr>
  <tr>
    <td><img src="screenshots/home.jpg" alt="Homepage" width="450"/></td>
    <td><img src="screenshots/product.jpg" alt="Product Detail" width="450"/></td>
  </tr>
  <tr>
    <td align="center"><b>Search & Price Filtering</b></td>
    <td align="center"><b>Interactive Shopping Cart</b></td>
  </tr>
  <tr>
    <td><img src="screenshots/filter.jpg" alt="Search & Filter" width="450"/></td>
    <td><img src="screenshots/cart.jpg" alt="Shopping Cart" width="450"/></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><b>Customized Admin Dashboard</b></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><img src="screenshots/admin.jpg" alt="Admin Dashboard" width="700"/></td>
  </tr>
</table>

---

## Key Features

### Customer Experience
- **Catalog Browsing**: Organized by categories (Mobiles, Laptops, Watches, Headphones) with responsive Owl Carousel sliders.
- **Search & Filtering**: Multi-field query search (title, description, brand) with category filters, dynamic min/max price sliders, and sorting (price low/high, popularity, newest).
- **Product Detail**: Product specifications table, thumbnail image gallery, stock availability badges, and related product recommendations.
- **Ratings & Reviews**: 1–5 star rating system with user reviews, average rating calculation, and verified purchase flags.
- **Interactive Shopping Cart**: Real-time AJAX item increment (`+`), decrement (`-`), and removal without full page reloads.
- **Wishlist**: Save and manage favorite items with one-click AJAX toggle.
- **Recently Viewed**: Session-backed tracking of recently browsed items.
- **Multi-Address Checkout**: Manage multiple delivery addresses and select preferred shipping address at checkout.
- **Order Lifecycle Tracking**: Step-by-step visual progress bar (`Pending` → `Accepted` → `Packed` → `On The Way` → `Delivered`).
- **Order Cancellation**: Self-service order cancellation before shipping.
- **Data Export**: Export order history directly to CSV format.

### Admin & Operations
- **Inventory & Stock Management**: Color-coded stock indicators (`In Stock`, `Low Stock`, `Out of Stock`) and quick out-of-stock bulk actions.
- **Promotions**: Bulk apply percentage discounts directly from the admin panel.
- **Order Processing**: Transition order states, view customer order summaries, and export filtered order records to CSV.
- **One-Command Data Seeding**: Custom management command (`python manage.py seed_data`) to populate the store with dummy products, specifications, and images.

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend Framework** | [Django 5.x](https://www.djangoproject.com/) (Python 3.11+) |
| **Database** | [SQLite](https://www.sqlite.org/) (default; production-ready for PostgreSQL via `DATABASE_URL`) |
| **Configuration** | [django-environ](https://github.com/joke2k/django-environ) for 12-Factor environment variable management |
| **Image Processing** | [Pillow](https://python-pillow.org/) |
| **Frontend** | HTML5, CSS3, [Bootstrap 5](https://getbootstrap.com/) |
| **UI Components** | [Owl Carousel](https://owlcarousel2.github.io/OwlCarousel2/), [Font Awesome 5](https://fontawesome.com/) |
| **JavaScript** | Vanilla JavaScript & [jQuery 3.7](https://jquery.com/) for AJAX requests |
| **Containerization** | Docker & Docker Compose |

---

## Project Architecture

```text
kart/
├── app/                        # Main Django Application
│   ├── management/commands/    # Custom commands (seed_data)
│   ├── migrations/             # Database migration history
│   ├── static/app/             # CSS, JS, SVGs, and bundled assets
│   ├── templates/app/          # Jinja/Django HTML templates
│   ├── tests/                  # Automated test suite (models, views, forms, urls)
│   ├── admin.py                # Admin panel customization & inlines
│   ├── forms.py                # Authentication & customer profile forms
│   ├── models.py               # Database schemas (Product, Cart, Order, Review, etc.)
│   ├── urls.py                 # Application URL routing
│   └── views.py                # Class-based and functional views
├── kart/                       # Project Configuration
│   ├── settings.py             # Django settings (configured via .env)
│   ├── urls.py                 # Root URL routing & media serving
│   ├── wsgi.py / asgi.py       # Application server entrypoints
├── media/                      # Uploaded product & profile images
├── screenshots/                # Showcase images for documentation
├── Dockerfile                  # Container build instructions
├── docker-compose.yml          # Container orchestration
├── entrypoint.sh               # Container startup script
├── requirements.txt            # Python dependencies
└── manage.py                   # Django CLI management script
```

---

## Getting Started

### Prerequisites
- **Python**: Version `3.10` or higher (tested on `3.11`)
- **Git**

### Local Installation (venv)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/santoshkkashyap25/kart-ecommerce.git
   cd kart-ecommerce
   ```

2. **Create and activate a virtual environment:**
   - On Windows (PowerShell):
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - On macOS / Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   *(The default `.env` comes pre-configured for local development with SQLite).*

5. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Seed the database with sample products:**
   ```bash
   python manage.py seed_data
   ```

7. **Create a superuser (for admin access):**
   ```bash
   python manage.py createsuperuser
   ```

8. **Start the development server:**
   ```bash
   python manage.py runserver
   ```
   - Storefront: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - Admin Panel: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

---

### Docker Installation

If you prefer running via Docker with automatic migration and data seeding:

```bash
# 1. Clone and enter directory
git clone https://github.com/santoshkkashyap25/kart-ecommerce.git
cd kart-ecommerce

# 2. Configure environment
cp .env.example .env

# 3. Build and run containers
docker-compose up -d --build
```
- Access the store at: [http://localhost:8000](http://localhost:8000)
- Default Docker admin: User `admin` | Password `adminpass`

---

## Environment Configuration

Configuration is managed via `.env` using `django-environ`:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DEBUG` | Enable Django debug mode | `True` |
| `SECRET_KEY` | Django cryptographic signing key | Required |
| `ALLOWED_HOSTS` | Comma-separated list of permitted hostnames | `localhost,127.0.0.1,0.0.0.0` |
| `DATABASE_URL` | *(Optional)* PostgreSQL connection string | Defaults to `db.sqlite3` |
| `DJANGO_SUPERUSER_USERNAME` | Username for automated setup | `admin` |
| `DJANGO_SUPERUSER_EMAIL` | Email for automated setup | `admin@test.com` |
| `DJANGO_SUPERUSER_PASSWORD` | Password for automated setup | `adminpass` |

---

## Automated Tests

The repository contains a comprehensive automated test suite covering models, views, forms, URL resolution, and session management:

```bash
# Run all tests
python manage.py test

# Run individual test modules
python manage.py test app.tests.test_models
python manage.py test app.tests.test_views
python manage.py test app.tests.test_forms
python manage.py test app.tests.test_urls
```
