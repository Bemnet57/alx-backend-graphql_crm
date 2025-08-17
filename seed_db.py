# seed_db.py (root)
import os
import django

# Point Django to your project settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "graphql_crm.settings")

django.setup()

from django.db import transaction
from crm.models import Customer, Product

def run():
    customers = [
        {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol", "email": "carol@example.com", "phone": None},
    ]

    products = [
        {"name": "Laptop", "price": 999.99, "stock": 10},
        {"name": "Mouse", "price": 19.99, "stock": 200},
        {"name": "Keyboard", "price": 49.99, "stock": 150},
    ]

    created_customers = []
    created_products = []

    with transaction.atomic():
        for c in customers:
            obj, _ = Customer.objects.get_or_create(
                email=c["email"],
                defaults={"name": c["name"], "phone": c["phone"]},
            )
            created_customers.append(obj)

        for p in products:
            obj, _ = Product.objects.get_or_create(
                name=p["name"],
                defaults={"price": p["price"], "stock": p["stock"]},
            )
            created_products.append(obj)

    print(f"Seeded {len(created_customers)} customers and {len(created_products)} products.")

if __name__ == "__main__":
    run()
