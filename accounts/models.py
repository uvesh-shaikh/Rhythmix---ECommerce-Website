from django.db import models
from base.models import BaseModel
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from base.email import sent_account_activation_mail
from products.models import Coupon, Product

# Create your models here.
class Profile(BaseModel):
   user = models.OneToOneField(User, on_delete=models.CASCADE,related_name="profile")
   is_email_verified = models.BooleanField(default=False)
   email_token = models.CharField(max_length=100, null=False, blank=True)
   profile_image = models.ImageField(upload_to='profile')

   def get_cart_count(self):
       return CartItems.objects.filter(cart__user = self.user, cart__is_paid= False).count()
   
   

class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name="cart")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL , related_name="coupon", null=True, blank=True)
    razor_pay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_signature = models.CharField(max_length=100, null=True, blank=True)
    is_paid = models.BooleanField(default=False)

    def get_cart_total(self):
        cart_items = self.cart_items.all()
        price=[]
        for cart_item in cart_items:
            price.append(cart_item.product.price*cart_item.itemQyt)

        if self.coupon:
            if self.coupon.minimum_price < sum(price):
                return sum(price) - self.coupon.discount_price


        return sum(price)
    


class CartItems(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    itemQyt =  models.PositiveIntegerField(default=1)
    def get_product_price(self):
        price = [self.product.price]

        return sum(price)*self.itemQyt
        # return self.product.price*self.itemQyt
    
    def get_product_count(self):
        count = self.itemQyt

        return count
        

class Order(BaseModel):
    name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length = 254)
    address = models.CharField(max_length=250, null=False, blank=False)
    city = models.CharField(max_length=100, null=False, blank=False)
    state = models.CharField(max_length=100, null=False, blank=False)
    zip_code = models.CharField(max_length=100, null=False, blank=False)
    phone = models.IntegerField() 



@receiver(post_save, sender = User)
def send_email_token(sender, instance, created ,**kwargs):
    try:
        if created:
            email_token = str(uuid.uuid4())
            Profile.objects.create(user=instance , email_token=email_token)
            email = instance.email
            sent_account_activation_mail(email, email_token)
    except Exception as e:
        print(e)
