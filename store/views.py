from django.shortcuts import render
from .models import Product, ProductGallery
from category.models import Category
from django.shortcuts import get_object_or_404
from carts.models import Cart, CartItem
from carts.views import _cart_id
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

# Create your views here.

def store(request, category_slug=None):

    categories = None
    products = None

    if category_slug != None:
            # fetch available products for a specific category
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        # fetch available products for a specific category
        paginator = Paginator(products, 3)
        # get the page number
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        
        product_count = products.count()
    else:
            # fetch available products for Home page
        products = Product.objects.all().filter(is_available=True).order_by('pk')
        # create paginator
        paginator = Paginator(products, 6)
        # get the page number
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        product_count = products.count()


    context = {
        # PASS PAGED PRODUCTS TO CONTEXT
        'products': paged_products, 
        'product_count': product_count,
    }
    
    return render(request, 'store/store.html', context)   



def product_detail(request, category_slug, product_slug):
    # TRY FIND PRODUCT BY CATEGORY AND PRODUCT SLUG
    try:
        # get single product
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        # check if product is in cart
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

    except Exception as e:
        raise e


    # GET THE PRODUCT GALLERY
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)



def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(description__icontains=keyword)
            product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)