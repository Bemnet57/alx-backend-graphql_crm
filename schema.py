# # #For projects implementing GraphQL 
# # # APIs with libraries like Graphene-Django, schema.py is where the GraphQL schema is defined, 
# # # including types, queries, mutations, and relationships.

import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(CRMQuery, graphene.ObjectType):
    pass

class Mutation(CRMMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)



# # import graphene

# # class Query(graphene.ObjectType):
# #     hello = graphene.String(default_value="Hello, GraphQL!")

# # schema = graphene.Schema(query=Query)

# import graphene
# from graphene_django import DjangoObjectType
# from django.db import transaction
# from django.core.exceptions import ValidationError
# from decimal import Decimal
# from django.utils import timezone
# import re

# from .models import Customer, Product, Order


# # ===== GraphQL Types =====
# class CustomerType(DjangoObjectType):
#     class Meta:
#         model = Customer
#         fields = ("id", "name", "email", "phone", "created_at")


# class ProductType(DjangoObjectType):
#     class Meta:
#         model = Product
#         fields = ("id", "name", "price", "stock")


# class OrderType(DjangoObjectType):
#     class Meta:
#         model = Order
#         fields = ("id", "customer", "products", "order_date", "total_amount")


# # ===== Validators =====
# PHONE_PATTERN = re.compile(r"^(\+\d{7,15}|\d{3}-\d{3}-\d{4})$")

# def validate_phone(phone):
#     if not phone:
#         return True
#     return bool(PHONE_PATTERN.match(phone))


# # ===== Mutation Inputs =====
# class CreateCustomerInput(graphene.InputObjectType):
#     name = graphene.String(required=True)
#     email = graphene.String(required=True)
#     phone = graphene.String()


# class BulkCustomerInput(graphene.InputObjectType):
#     name = graphene.String(required=True)
#     email = graphene.String(required=True)
#     phone = graphene.String()


# class CreateProductInput(graphene.InputObjectType):
#     name = graphene.String(required=True)
#     price = graphene.Float(required=True)
#     stock = graphene.Int(default_value=0)


# class CreateOrderInput(graphene.InputObjectType):
#     customer_id = graphene.ID(required=True)
#     product_ids = graphene.List(graphene.ID, required=True)
#     order_date = graphene.DateTime()


# # ===== Mutations =====
# class CreateCustomer(graphene.Mutation):
#     class Arguments:
#         input = CreateCustomerInput(required=True)

#     customer = graphene.Field(CustomerType)
#     message = graphene.String()

#     @classmethod
#     def mutate(cls, root, info, input):
#         if Customer.objects.filter(email__iexact=input.email).exists():
#             return cls(message="Email already exists.")

#         if not validate_phone(input.phone):
#             return cls(message="Invalid phone format.")

#         customer = Customer(
#             name=input.name,
#             email=input.email,
#             phone=input.phone
#         )
#         customer.save()
#         return cls(customer=customer, message="Customer created successfully.")


# class BulkCreateCustomers(graphene.Mutation):
#     class Arguments:
#         input = graphene.List(BulkCustomerInput, required=True)

#     customers = graphene.List(CustomerType)
#     errors = graphene.List(graphene.String)

#     @classmethod
#     def mutate(cls, root, info, input):
#         created_customers = []
#         errors = []

#         with transaction.atomic():
#             for idx, data in enumerate(input):
#                 if Customer.objects.filter(email__iexact=data.email).exists():
#                     errors.append(f"[{idx}] Email already exists: {data.email}")
#                     continue
#                 if not validate_phone(data.phone):
#                     errors.append(f"[{idx}] Invalid phone format: {data.phone}")
#                     continue
#                 customer = Customer(
#                     name=data.name,
#                     email=data.email,
#                     phone=data.phone
#                 )
#                 customer.save()
#                 created_customers.append(customer)

#         return cls(customers=created_customers, errors=errors)


# class CreateProduct(graphene.Mutation):
#     class Arguments:
#         input = CreateProductInput(required=True)

#     product = graphene.Field(ProductType)

#     @classmethod
#     def mutate(cls, root, info, input):
#         if input.price <= 0:
#             raise ValidationError("Price must be positive")
#         if input.stock < 0:
#             raise ValidationError("Stock cannot be negative")
#         product = Product(
#             name=input.name,
#             price=Decimal(str(input.price)),
#             stock=input.stock
#         )
#         product.save()
#         return cls(product=product)


# class CreateOrder(graphene.Mutation):
#     class Arguments:
#         input = CreateOrderInput(required=True)

#     order = graphene.Field(OrderType)
#     message = graphene.String()

#     @classmethod
#     def mutate(cls, root, info, input):
#         try:
#             customer = Customer.objects.get(pk=input.customer_id)
#         except Customer.DoesNotExist:
#             return cls(message="Invalid customer ID.")

#         products = list(Product.objects.filter(pk__in=input.product_ids))
#         if not products:
#             return cls(message="No valid products found.")

#         order = Order(customer=customer, order_date=input.order_date or timezone.now())
#         order.save()
#         order.products.set(products)
#         order.total_amount = sum([p.price for p in products])
#         order.save()

#         return cls(order=order, message="Order created successfully.")


# # ===== Root Query & Mutation =====
# class Query(graphene.ObjectType):
#     customers = graphene.List(CustomerType)
#     products = graphene.List(ProductType)
#     orders = graphene.List(OrderType)

#     def resolve_customers(root, info):
#         return Customer.objects.all()

#     def resolve_products(root, info):
#         return Product.objects.all()

#     def resolve_orders(root, info):
#         return Order.objects.all()


# class Mutation(graphene.ObjectType):
#     create_customer = CreateCustomer.Field()
#     bulk_create_customers = BulkCreateCustomers.Field()
#     create_product = CreateProduct.Field()
#     create_order = CreateOrder.Field()
