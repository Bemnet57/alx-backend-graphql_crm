# # import re
# # from decimal import Decimal, ROUND_HALF_UP
# # import graphene
# # from graphene_django import DjangoObjectType
# # from django.db import transaction
# # from django.core.exceptions import ValidationError
# # from django.utils import timezone

# # from .models import Customer, Product, Order


# # # --------------------
# # # GraphQL Types
# # # --------------------
# # class CustomerType(DjangoObjectType):
# #     class Meta:
# #         model = Customer
# #         fields = ("id", "name", "email", "phone", "created_at")


# # class ProductType(DjangoObjectType):
# #     class Meta:
# #         model = Product
# #         fields = ("id", "name", "price", "stock")


# # class OrderType(DjangoObjectType):
# #     class Meta:
# #         model = Order
# #         fields = ("id", "customer", "products", "order_date", "total_amount")


# # # --------------------
# # # Helpers / Validators
# # # --------------------
# # PHONE_PATTERN = re.compile(r"^(\+\d{7,15}|\d{3}-\d{3}-\d{4})$")

# # def validate_phone(phone: str) -> bool:
# #     if phone in (None, "",):
# #         return True
# #     return bool(PHONE_PATTERN.match(phone))

# # def quantize_money(value: Decimal) -> Decimal:
# #     return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# # # --------------------
# # # CreateCustomer
# # # --------------------
# # class CreateCustomer(graphene.Mutation):
# #     class Arguments:
# #         name = graphene.String(required=True)
# #         email = graphene.String(required=True)
# #         phone = graphene.String()

# #     ok = graphene.Boolean()
# #     message = graphene.String()
# #     customer = graphene.Field(CustomerType)

# #     @classmethod
# #     def mutate(cls, root, info, name, email, phone=None):
# #         # Email uniqueness (friendly error)
# #         if Customer.objects.filter(email__iexact=email).exists():
# #             return CreateCustomer(ok=False, message="Email already exists.", customer=None)

# #         # Phone validation
# #         if not validate_phone(phone):
# #             return CreateCustomer(ok=False, message="Invalid phone format. Use +1234567890 or 123-456-7890.", customer=None)

# #         customer = Customer(name=name, email=email, phone=phone)
# #         try:
# #             customer.full_clean()  # model-level validation (e.g., EmailField)
# #             customer.save()
# #         except ValidationError as e:
# #             return CreateCustomer(ok=False, message="; ".join(sum(e.message_dict.values(), [])), customer=None)

# #         return CreateCustomer(ok=True, message="Customer created successfully.", customer=customer)


# # # --------------------
# # # BulkCreateCustomers (partial success with savepoints)
# # # --------------------
# # class CustomerInput(graphene.InputObjectType):
# #     name = graphene.String(required=True)
# #     email = graphene.String(required=True)
# #     phone = graphene.String()


# # class CustomerErrorType(graphene.ObjectType):
# #     index = graphene.Int()                 # index in the input list
# #     messages = graphene.List(graphene.String)


# # class BulkCreateCustomers(graphene.Mutation):
# #     class Arguments:
# #         customers = graphene.List(CustomerInput, required=True)

# #     ok = graphene.Boolean()                             # True if no errors at all
# #     created = graphene.List(CustomerType)               # successfully created customers
# #     errors = graphene.List(CustomerErrorType)           # per-record errors

# #     @classmethod
# #     def mutate(cls, root, info, customers):
# #         created_objs = []
# #         errors = []

# #         # One outer transaction for consistency; savepoints for partial success.
# #         with transaction.atomic():
# #             for idx, data in enumerate(customers):
# #                 sp_id = transaction.savepoint()
# #                 msgs = []

# #                 name = (data.get("name") or "").strip()
# #                 email = (data.get("email") or "").strip()
# #                 phone = (data.get("phone") or None)

# #                 if not name:
# #                     msgs.append("Name is required.")
# #                 if not email:
# #                     msgs.append("Email is required.")
# #                 elif Customer.objects.filter(email__iexact=email).exists():
# #                     msgs.append("Email already exists.")
# #                 if not validate_phone(phone):
# #                     msgs.append("Invalid phone format. Use +1234567890 or 123-456-7890.")

# #                 if msgs:
# #                     transaction.savepoint_rollback(sp_id)
# #                     errors.append(CustomerErrorType(index=idx, messages=msgs))
# #                     continue

# #                 try:
# #                     obj = Customer(name=name, email=email, phone=phone)
# #                     obj.full_clean()
# #                     obj.save()
# #                     transaction.savepoint_commit(sp_id)
# #                     created_objs.append(obj)
# #                 except ValidationError as e:
# #                     transaction.savepoint_rollback(sp_id)
# #                     flat_msgs = []
# #                     for field_msgs in e.message_dict.values():
# #                         flat_msgs.extend(field_msgs)
# #                     errors.append(CustomerErrorType(index=idx, messages=flat_msgs))

# #         ok = len(errors) == 0
# #         return BulkCreateCustomers(ok=ok, created=created_objs, errors=errors)


# # # --------------------
# # # CreateProduct
# # # --------------------
# # class CreateProduct(graphene.Mutation):
# #     class Arguments:
# #         name = graphene.String(required=True)
# #         price = graphene.Float(required=True)  # accept float input; store as Decimal
# #         stock = graphene.Int(required=False)   # default 0

# #     ok = graphene.Boolean()
# #     message = graphene.String()
# #     product = graphene.Field(ProductType)

# #     @classmethod
# #     def mutate(cls, root, info, name, price, stock=0):
# #         msgs = []
# #         if price is None or float(price) <= 0:
# #             msgs.append("Price must be a positive number.")
# #         if stock is None:
# #             stock = 0
# #         if int(stock) < 0:
# #             msgs.append("Stock cannot be negative.")

# #         if msgs:
# #             return CreateProduct(ok=False, message="; ".join(msgs), product=None)

# #         product = Product(
# #             name=name.strip(),
# #             price=quantize_money(Decimal(str(price))),
# #             stock=int(stock),
# #         )
# #         try:
# #             product.full_clean()
# #             product.save()
# #         except ValidationError as e:
# #             return CreateProduct(ok=False, message="; ".join(sum(e.message_dict.values(), [])), product=None)

# #         return CreateProduct(ok=True, message="Product created successfully.", product=product)


# # # --------------------
# # # CreateOrder
# # # --------------------
# # class CreateOrder(graphene.Mutation):
# #     class Arguments:
# #         customer_id = graphene.ID(required=True)
# #         product_ids = graphene.List(graphene.ID, required=True)
# #         order_date = graphene.DateTime(required=False)  # defaults to now

# #     ok = graphene.Boolean()
# #     message = graphene.String()
# #     order = graphene.Field(OrderType)

# #     @classmethod
# #     def mutate(cls, root, info, customer_id, product_ids, order_date=None):
# #         # Validate customer
# #         try:
# #             customer = Customer.objects.get(pk=int(customer_id))
# #         except (Customer.DoesNotExist, ValueError):
# #             return CreateOrder(ok=False, message="Invalid customer ID.", order=None)

# #         # Validate products
# #         if not product_ids:
# #             return CreateOrder(ok=False, message="Select at least one product.", order=None)

# #         # Normalize IDs and ensure all exist
# #         try:
# #             ids = [int(pid) for pid in product_ids]
# #         except ValueError:
# #             return CreateOrder(ok=False, message="One or more product IDs are invalid.", order=None)

# #         products = list(Product.objects.filter(pk__in=ids))
# #         missing_ids = set(ids) - set(p.id for p in products)
# #         if missing_ids:
# #             return CreateOrder(
# #                 ok=False,
# #                 message=f"Invalid product ID(s): {', '.join(map(str, sorted(missing_ids)))}",
# #                 order=None
# #             )

# #         # Create order and calculate total_amount accurately from DB prices
# #         when = order_date or timezone.now()
# #         with transaction.atomic():
# #             order = Order.objects.create(customer=customer, order_date=when)
# #             order.products.set(products)

# #             total = sum((p.price for p in products), Decimal("0.00"))
# #             order.total_amount = quantize_money(total)
# #             order.save()

# #         return CreateOrder(ok=True, message="Order created successfully.", order=order)


# # # --------------------
# # # Root Query & Mutation
# # # --------------------
# # class Query(graphene.ObjectType):
# #     customers = graphene.List(CustomerType)
# #     products = graphene.List(ProductType)
# #     orders = graphene.List(OrderType)

# #     def resolve_customers(root, info):
# #         return Customer.objects.all().order_by("-id")

# #     def resolve_products(root, info):
# #         return Product.objects.all().order_by("-id")

# #     def resolve_orders(root, info):
# #         return Order.objects.select_related("customer").prefetch_related("products").order_by("-id")


# # class Mutation(graphene.ObjectType):
# #     create_customer = CreateCustomer.Field()
# #     bulk_create_customers = BulkCreateCustomers.Field()
# #     create_product = CreateProduct.Field()
# #     create_order = CreateOrder.Field()


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


import re
import graphene
from graphene_django import DjangoObjectType
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import Customer, Product, Order


# ----------------------
# GraphQL Types
# ----------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "order_date", "total_amount")


# ----------------------
# Validators
# ----------------------
PHONE_PATTERN = re.compile(r"^(\+\d{7,15}|\d{3}-\d{3}-\d{4})$")

def validate_phone(phone: str) -> bool:
    if not phone:
        return True
    return bool(PHONE_PATTERN.match(phone))


# ----------------------
# Input Types
# ----------------------
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(default_value=0)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# ----------------------
# Mutations
# ----------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        # Check unique email
        if Customer.objects.filter(email__iexact=input.email).exists():
            return cls(message="Email already exists")

        # Validate phone
        if not validate_phone(input.phone):
            return cls(message="Invalid phone format. Use +1234567890 or 123-456-7890")

        customer = Customer(name=input.name, email=input.email, phone=input.phone)
        try:
            customer.full_clean()
            customer.save()
        except ValidationError as e:
            return cls(message="; ".join(sum(e.message_dict.values(), [])))

        return cls(customer=customer, message="Customer created successfully")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @classmethod
    def mutate(cls, root, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for idx, data in enumerate(input):
                if Customer.objects.filter(email__iexact=data.email).exists():
                    errors.append(f"[{idx}] Email already exists: {data.email}")
                    continue
                if not validate_phone(data.phone):
                    errors.append(f"[{idx}] Invalid phone format: {data.phone}")
                    continue

                try:
                    customer = Customer(name=data.name, email=data.email, phone=data.phone)
                    customer.full_clean()
                    customer.save()
                    created_customers.append(customer)
                except ValidationError as e:
                    flat_errors = "; ".join(sum(e.message_dict.values(), []))
                    errors.append(f"[{idx}] {flat_errors}")

        return cls(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        if input.price <= 0:
            return cls(message="Price must be positive")
        if input.stock < 0:
            return cls(message="Stock cannot be negative")

        product = Product(
            name=input.name,
            price=Decimal(str(input.price)),
            stock=input.stock
        )
        try:
            product.full_clean()
            product.save()
        except ValidationError as e:
            return cls(message="; ".join(sum(e.message_dict.values(), [])))

        return cls(product=product, message="Product created successfully")


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    message = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        # Validate customer
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            return cls(message="Invalid customer ID")

        # Validate products
        if not input.product_ids:
            return cls(message="At least one product must be selected")

        products = list(Product.objects.filter(pk__in=input.product_ids))
        missing_ids = set(map(int, input.product_ids)) - {p.id for p in products}
        if missing_ids:
            return cls(message=f"Invalid product ID(s): {', '.join(map(str, missing_ids))}")

        # Create order
        order = Order(customer=customer, order_date=input.order_date or timezone.now())
        order.save()
        order.products.set(products)

        # Ensure total_amount is accurate
        total = sum([p.price for p in products], Decimal("0.00"))
        order.total_amount = total
        order.save()

        return cls(order=order, message="Order created successfully")


# ----------------------
# Root Query & Mutation
# ----------------------
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
