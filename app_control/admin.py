from django.contrib import admin
from .models import InventoryGroup, Inventory

admin.register((Inventory, InventoryGroup, ))