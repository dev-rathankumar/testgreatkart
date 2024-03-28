from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product

def home(request):

    # fetch available products for Home page
    products = Product.objects.all().filter(is_available=True).order_by('created_date')

    context = {
        'products': products, 
    }



    return render(request, 'home.html', context)