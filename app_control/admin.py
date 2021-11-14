from django.contrib import admin
from .models import InventoryGroup, Inventory, Shop

admin.register((Inventory, InventoryGroup, Shop, ))