from django.db import models
import enum
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

class TransactionType(models.TextChoices):
    IN = 'IN', 'Приход'
    OUT = 'OUT', 'Расход'

class OrderStatus(models.TextChoices):
    NEW = 'NEW', 'Новый'
    SHIPPED = 'SHIPPED', 'Отгружен'
    CANCELLED = 'CANCELLED', 'Отменен'

class Categories(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey("self", on_delete=models.CASCADE,null=True, blank=True, related_name="children")
    def __str__(self):
        return self.name


class Products(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(unique=True, max_length=50)
    category = models.ForeignKey(Categories, related_name="products", on_delete=models.PROTECT,)
    unit = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.sku})"

class Warehouses(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    capacity = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Suppliers(models.Model):
    name = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=20, validators=[
            RegexValidator(
                regex=r'^\+375\d{9}$',
                message='Телефон должен быть в формате +375 XX XXX XX XX'
            )
        ])
    email = models.EmailField(default=" ")

    def __str__(self):
        return self.name


class Batches(models.Model):
    product = models.ForeignKey(Products, related_name="batches", on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouses, related_name="batches", on_delete=models.CASCADE)
    supplier = models.ForeignKey(Suppliers, related_name="batches", on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0)
    purchase_price = models.FloatField(default=0)
    expire_date = models.DateField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Transactions(models.Model):
    batch = models.ForeignKey(Batches, related_name="transactions", on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=TransactionType.choices)
    quantity = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(get_user_model(), related_name="transactions", on_delete=models.SET_NULL, null=True)
    comment = models.TextField(blank=True)


class Orders(models.Model):
    customer_name = models.CharField(max_length=255)
    status = models.CharField(choices=OrderStatus.choices, max_length=10, default=OrderStatus.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    shipped_at = models.DateTimeField(blank=True)

class OrderItems(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name="order_items")
    quantity_requested = models.IntegerField(default=0)
    quantity_fullfilled = models.IntegerField(default=0)