from django.contrib import admin
from .models import Profile, Cart, CartItems,Order

# Register your models here.

admin.site.register(Profile)
admin.site.register(Cart)
admin.site.register(CartItems)
admin.site.register(Order)
