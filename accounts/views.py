from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Profile, Cart, CartItems, Coupon,Order
from products.models import Product
import razorpay
from django.conf import settings


# Create your views here.

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username = email)
        if not user_obj.exists():
            messages.warning(request, "User not found..")
            return HttpResponseRedirect(request.path_info)
        
        if not user_obj[0].profile.is_email_verified:
            messages.warning(request, "Please verify your email..")
            return HttpResponseRedirect(request.path_info)

        user_obj = authenticate(request, username = email, password = password)

        if user_obj :
            login(request, user_obj)
            return redirect('/')
        
        messages.warning(request, "Invalid credentials..")
        return HttpResponseRedirect(request.path_info)
        
    return render(request,'Accounts/login_page.html')


def logout_page(request):
    if request.user:
        logout(request)
        messages.success(request, "Logout successfully")
        # return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return redirect('/')


def register(request):
    if request.method == 'POST':
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        email = request.POST.get('email')
        password = request.POST.get('password')
        # print(request.POST)
        user_obj = User.objects.filter(username = email)
        print("usser object")
        print(user_obj)
        if user_obj.exists():
            messages.warning(request, "User already exists..")
            return HttpResponseRedirect(request.path_info)
        user_obj = User.objects.create(first_name=first_name, last_name=last_name, email=email, username=email)
        user_obj.set_password(password)
        user_obj.save()
        # print(user_obj.get_full_name())
        messages.success(request, "User created successfully..")
        return HttpResponseRedirect(request.path_info)
    return render(request,'Accounts/register.html')


def activate_mail(request, email_token):
    try:
        user = Profile.objects.get(email_token = email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse("not verified")
    

def add_to_cart(request, uid):
    if request.user.is_authenticated:
        product = Product.objects.get(uid = uid)
        user = request.user
        cart, _ = Cart.objects.get_or_create(user = user, is_paid = False)
        cart_item = CartItems.objects.create(cart = cart, product=product)
        cart_item.save()
    else:
        messages.warning(request, "Login required")
        return redirect('/accounts/login')
    # print(CartItems.objects.all().count())

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
      

def get_cards(request):
    cart_obj = None
    try:
        if request.user.is_authenticated:
            cart_obj =  Cart.objects.get(is_paid=False , user = request.user)
            print(cart_obj.cart_items.get())
        else:
            messages.warning(request, "Login Required")
            return redirect('/accounts/login')


    except Exception as e:
        print(e)
    if request.method=='POST':
        coupon = request.POST.get("coupon")
        coupon_obj = Coupon.objects.filter(coupon_code__icontains = coupon)
        if not coupon_obj.exists():
            messages.warning(request, "Invalid coupon")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if cart_obj.coupon:
            messages.warning(request, "Coupon already applied")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if cart_obj.get_cart_total() < coupon_obj[0].minimum_price:
            messages.warning(request, f'Amount should be greater than{coupon_obj[0].minimum_price}')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        if coupon_obj[0].is_expired:
            messages.warning(request, "This coupon has been expired")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        cart_obj.coupon = coupon_obj[0]
        cart_obj.save()
        messages.success(request, "Coupon applied")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    

    context = {'cart': cart_obj }
    return render(request, 'Accounts/carts.html', context)


    

def remove_cart(request, cart_item_id):
    try:
        cart_item = CartItems.objects.get(uid = cart_item_id)
        cart_item.delete()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_coupon(request, uid):
    cart = Cart.objects.get(uid = uid) 
    cart.coupon = None
    cart.save()
    messages.success(request, "Coupon Removed")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def success(request):
    order_id = request.GET.get('razorpay_order_id')
    cart_obj = Cart.objects.get(razor_pay_order_id = order_id)
    cart_obj.is_paid = True
    cart_obj.save()
    messages.success(request, "Payment Successfull")
    return redirect('/')
    # return HttpResponse("Payment Success")


def update_cart(request, cart_item_id,action):
    try:
        cart_item = CartItems.objects.get(uid = cart_item_id)
        if action=='add':
            cart_item.itemQyt+=1
        elif action == 'remove':
            cart_item.itemQyt -= 1
            if  cart_item.itemQyt == 0:
                cart_item.delete()
        cart_item.save()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def checkout(request):
    cart_obj = None
    try:
        cart_obj = Cart.objects.get(is_paid=False , user = request.user)
    except Exception as e:
        print(e)
    if cart_obj and cart_obj.get_cart_total() * 100 > 0:
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_KEY_SECRET))
        payment = client.order.create({'amount': cart_obj.get_cart_total() * 100, 'currency': 'INR', 'payment_capture':1})
        cart_obj.razor_pay_order_id = payment['id']
        cart_obj.save()
    else:
        payment = None  
    context = {'cart': cart_obj ,'payment': payment}
    if request.method=='POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address = request.POST.get('address1') + request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        order = Order(name=name, email=email, address = address, city=city, state=state, zip_code=zip_code, phone=phone)
        order.save()
        return render(request, 'Checkout/payment.html',context)

    
    # context = {'cart': cart_obj ,'payment': payment}
    return render(request, 'Checkout/checkout.html', context)
    # context = {'cart' : cart_obj}
    # return render(request, 'Checkout/checkout.html',context)
