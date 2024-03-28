from .models import Cart, CartItem
from .views import _cart_id

# Create a context processor to access cart count from any template

# without having to pass it to the context of every view

# The context processor is a function that takes a request object as an argument

# The context processor must be added to the TEMPLATES setting in the settings.py file

# under the OPTIONS key

# The context processor function is added to the context_processors list


def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    else:
        try:
            # Fetch the cart
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            
                # If the user is authenticated, fetch the users cart items
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                # IF the user is not authenticated, fetch the cart items using the cart_id present in the session
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
            # Loop through the cart items and count the quantity
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_count = 0

    return dict(cart_count=cart_count)