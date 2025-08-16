"""
Seed script for alx-backend-graphql_crm
Run with:
    python manage.py shell < seed_db.py
"""

from decimal import Decimal
from django.utils import timezone
from crm.models import Customer, Product, Order


# --- Clear old data (optional) ---
Order.objects.all().delete()
Product.objects.all().delete()
Customer.objects.all().delete()


# --- Create Customers ---
alice = Customer.objects.create(
    name="Alice Johnson",
    email="alice@example.com",
    phone="+1234567890"
)

bob = Customer.objects.create(
    name="Bob Smith",
    email="bob@example.com",
    phone="123-456-7890"
)

carol = Customer.objects.create(
    name="Carol White",
    email="carol@example.com"
)


# --- Create Products ---
laptop = Product.objects.create(
    name="Laptop",
    price=Decimal("999.99"),
    stock=10
)

phone = Product.objects.create(
    name="Smartphone",
    price=Decimal("499.99"),
    stock=25
)

headphones = Product.objects.create(
    name="Headphones",
    price=Decimal("199.99"),
    stock=50
)


# --- Create Orders ---
order1 = Order.objects.create(
    customer=alice,
    order_date=timezone.now(),
    total_amount=laptop.price + phone.price
)
order1.products.set([laptop, phone])

order2 = Order.objects.create(
    customer=bob,
    order_date=timezone.now(),
    total_amount=headphones.price
)
order2.products.set([headphones])


print("✅ Database seeded successfully!")
print(f"Customers: {Customer.objects.count()}")
print(f"Products: {Product.objects.count()}")
print(f"Orders: {Order.objects.count()}")
