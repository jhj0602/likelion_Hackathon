from django.contrib import admin
from .models import itemsaved,wear_mywear,CustomUser
# Register your models here.
admin.site.register(itemsaved)
admin.site.register(wear_mywear)
admin.site.register(CustomUser)