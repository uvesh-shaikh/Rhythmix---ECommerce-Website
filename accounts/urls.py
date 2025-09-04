from django.urls import path,include
from accounts.views import *
# success, register, login_page, logout_page ,activate_mail, get_cards, add_to_cart, remove_cart, remove_coupon,update_cart


urlpatterns = [
    path('register/',register,name="register"),
    path('login/',login_page,name="login"),
    path('logout/',logout_page,name="logout"),
    path('activate/<email_token>/', activate_mail, name="activate_mail"),
    path('cards/', get_cards, name="cards"),
    path('add-to-cart/<uid>', add_to_cart, name = "add_to_cart"),
    path('remove-cart/<cart_item_id>', remove_cart, name = "remove_cart"),
    path('remove-coupon/<uid>', remove_coupon, name = "remove_coupon"),
    path('success/', success, name = "success"),

    path('update-cart/<uuid:cart_item_id>/<str:action>', update_cart, name = "update_cart"),
    path('checkout/', checkout, name="checkout"),

    

]