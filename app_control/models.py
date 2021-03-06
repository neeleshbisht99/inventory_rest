from django.db import models
from user_control.models import (CustomUser, )
from user_control.views import add_user_activity


class InventoryGroup(models.Model):
    created_by = models.ForeignKey(
        CustomUser, null=True, on_delete=models.SET_NULL, related_name="inventory_groups")
    name = models.CharField(max_length=100, unique=True)
    belongs_to = models.ForeignKey(
        'self', null=True, on_delete=models.SET_NULL, related_name="group_relations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering=("-created_at", )

    def init(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_name = self.name

    def save(self, *args, **kwargs):
        action = f"added new group - '{self.name}'"
        if self.pk is not None:
            action = f"updated group from - '{self.old_name}' to '{self.name}'"
        super.save(*args, **kwargs)
        add_user_activity(self.created_by, action=action)

    def delete(self, *args, **kwargs):
        created_by = self.created_by
        action = f"deleted group - '{self.name}'"
        super.delete(*args, **kwargs)
        add_user_activity(created_by, action=action)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    created_by = models.ForeignKey(
        CustomUser, null=True, on_delete=models.SET_NULL, related_name="inventory_items")
    code = models.CharField(max_length=100, unique=True, null=True)
    photo = models.TextField(blank=True, null=True)
    group = models.ForeignKey(
        InventoryGroup, null=True, on_delete=models.SET_NULL, related_name="inventories"
    )
    total = models.PositiveIntegerField()
    remaining = models.PositiveIntegerField(null=True)
    name = models.CharField(max_length=255)
    price = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", )

    def init(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_name = self.name

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.remaining = self.total

        super.save(*args, **kwargs)

        if is_new:
            id_length = len(str(self.id))
            code_length = 6 - id_length
            zeroes = "".join("0" for i in range(code_length))
            self.code = f"BOSE{zeroes}{self.id}"

        action = f"added new inventory item with code - '{self.code}'"

        if not is_new:
            action = f"updated inventory item with code - '{self.code}'"
        add_user_activity(self.created_by, action=action)

    def delete(self, *args, **kwargs):
        created_by = self.created_by
        action = f"deleted inventory - '{self.name}'"
        super.delete(*args, **kwargs)
        add_user_activity(created_by, action=action)

    def __str__(self):
        return f"{self.name} - {self.code}"


class Shop(models.Model):
    created_by = models.ForeignKey(
        CustomUser, null=True, on_delete=models.SET_NULL, related_name="shops")
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at", )

    def init(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_name = self.name

    def save(self, *args, **kwargs):
        action = f"added new shop - '{self.name}'"
        if self.pk is not None:
            action = f"updated shop from - '{self.old_name}' to '{self.name}'"
        super.save(*args, **kwargs)
        add_user_activity(self.created_by, action=action)

    def delete(self, *args, **kwargs):
        created_by = self.created_by
        action = f"deleted shop - '{self.name}'"
        super.delete(*args, **kwargs)
        add_user_activity(created_by, action=action)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    created_by = models.ForeignKey(
        CustomUser, null=True, on_delete=models.SET_NULL, related_name="invoices")
    shop = models.ForeignKey(Shop, null=True, on_delete=models.SET_NULL, related_name="sale_shop")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", )

    def save(self, *args, **kwargs):
        action = f"added new invoice - '{self.name}'"
        super.save(*args, **kwargs)
        add_user_activity(self.created_by, action=action)

    def delete(self, *args, **kwargs):
        created_by = self.created_by
        action = f"deleted invoice - '{self.name}'"
        super.delete(*args, **kwargs)
        add_user_activity(created_by, action=action)

    def __str__(self):
        return self.name


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="invoice_items")
    item = models.ForeignKey(
        Inventory, null=True, on_delete=models.SET_NULL, related_name="inventory_invoices"
    )
    item_name = models.CharField(max_length=255, null=True)
    item_code = models.CharField(max_length=20, null=True)
    quantity = models.PositiveIntegerField()
    amount = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", )

    def save(self, *args, **kwargs):
        if self.item.remaining < self.quantity:
            raise Exception(f"item with code {self.item.code} does not have enough quantity")
        self.item_name = self.item.name
        self.item_code = self.item.code
        self.amount = self.quantity * self.item.price
        self.item.remaining = self.item.remaining - self.quantity
        self.item.save()
        super.save(*args, **kwargs)

    def __str__(self):
        return f"{self.item_code} - {self.quantity}"


















