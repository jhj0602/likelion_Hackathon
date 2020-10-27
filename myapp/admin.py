from django.contrib import admin
from .models import itemsaved,CustomUser,CartItem
# Register your models here.
admin.site.register(itemsaved)

admin.site.register(CustomUser)
admin.site.register(CartItem)