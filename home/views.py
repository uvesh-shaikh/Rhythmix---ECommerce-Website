from django.shortcuts import render
from products.models import Product, Category

# Create your views here.

def index(request):
    context = {'products': Product.objects.all()}
    return render(request, 'Home/index.html', context)
