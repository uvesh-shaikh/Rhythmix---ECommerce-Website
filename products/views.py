from django.shortcuts import render
from accounts.models import Cart
from products.models import Product


# Create your views here.

def get_product(request, slug):

    try:
        product = Product.objects.get(slug=slug)
        context = {'product': product}
        if request.GET.get('size'):
            size = request.GET.get('size')
            # print(size)
            price = product.get_price_by_size(size)
            # context['updated_price'] = price
            context['selected_size'] = size

        return render(request, 'Product/product.html', context=context)
    except Exception as e:
        print(e)

   







