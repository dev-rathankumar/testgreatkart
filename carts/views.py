from django.shortcuts import render
from store.models import Product, Variation
from .models import Cart, CartItem
from django.shortcuts import redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.



# FIND OR CREATE SESSION FOR CART
def _cart_id(request):
    # Retrieve the current session key (cart_id) from the request's session.
    cart = request.session.session_key

    # Check if the cart_id is not available (session is new or expired).
    if not cart:
        # If cart_id is not available, create a new session and obtain its key.
        cart = request.session.create()

    # Return the obtained or newly created cart_id.
    return cart




# ADD CART VIEW
def add_cart(request, product_id):
    # GET THE CURRENT USER
    current_user = request.user
    # GET THE PRODUCT
    product = Product.objects.get(id=product_id)

# IF USER IS AUTHENTICATED
    if current_user.is_authenticated:
        # LIST OF VARIATIONS - IF ANY - TO BE ADDED TO CART
        product_variation = [] 

        # CHECK IF VARIATION EXISTS - IF YES, ADD TO CART
        if request.method == 'POST': 
            for item in request.POST:
                key = item 
                value = request.POST[key] 
                try:
                    # get variation by key and value
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    # append to product_variation list
                    product_variation.append(variation)
                    print(product_variation)
                except:
                    pass
        # if cart item already exists in cart
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()

        # CHECK IF ITEM EXISTS IN CART
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id = []

            # GET EXISTING VARIATIONS
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            # IF CURRENT VARIAION EXISTS IN EXISTING VARIATIONS - APPEND TO EX_VAR_LIST

            if product_variation in ex_var_list:
                # GET THE INDEX OF THAT VARIATION
                index = ex_var_list.index(product_variation)
                # GET THE ID OF THAT CART ITEM
                item_id = id[index] 
                # GET THE CART ITEM WITH THAT ID
                item = CartItem.objects.get(product=product, id=item_id)
                # increase the cart item quantity
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                # check if cart item with same variation already exists
                if len(product_variation) > 0:
                    item.variations.clear()
                    # IF VARIATION EXISTS - ADD TO CART
                    item.variations.add(*product_variation)

                item.save()
            
        # IF ITEM DOES NOT EXIST IN CART - CREATE NEW CART ITEM
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                user = current_user
            )
            # CLEAR OLD CART AND ADD NEW VARIATION/S

            if len(product_variation) > 0:
                cart_item.variations.clear()
                for item in product_variation:
                    cart_item.variations.add(item)
            cart_item.save()

        return redirect('cart')



# IF USER NOT AUTHENTICATED
    else:
        # LIST OF VARIATIONS - IF ANY - TO BE ADDED TO CART
        product_variation = [] 

        # CHECK IF VARIATION EXISTS - IF YES, ADD TO CART
        if request.method == 'POST': 
            for item in request.POST:
                key = item 
                value = request.POST[key] 
                try:
                    # get variation by key and value
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    # append to product_variation list
                    product_variation.append(variation)
                    print(product_variation)
                except:
                    pass

        # CHECK IF CART EXISTS
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get cart using the cart_id from session

        # if cart does not exist
        except Cart.DoesNotExist:
            # create a new cart
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        # AFTER CHECKING IF CART EXISTS (OR CREATING ONE ) - ADD ITEM TO CART
        


        # if cart item already exists in cart
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

        # CHECK IF ITEM EXISTS IN CART
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing variations
            # item_id
            ex_var_list = []
            id = []

            # GET EXISTING VARIATIONS
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            # IF CURRENT VARIAION EXISTS IN EXISTING VARIATIONS - APPEND TO EX_VAR_LIST

            if product_variation in ex_var_list:
                # GET THE INDEX OF THAT VARIATION
                index = ex_var_list.index(product_variation)
                # GET THE ID OF THAT CART ITEM
                item_id = id[index] 
                # GET THE CART ITEM WITH THAT ID
                item = CartItem.objects.get(product=product, id=item_id)
                # increase the cart item quantity
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                # check if cart item with same variation already exists
                if len(product_variation) > 0:
                    item.variations.clear()
                    # IF VARIATION EXISTS - ADD TO CART
                    item.variations.add(*product_variation)

                item.save()
            
        # IF ITEM DOES NOT EXIST IN CART - CREATE NEW CART ITEM
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = 1,
                cart = cart
            )
            # CLEAR OLD CART AND ADD NEW VARIATION/S

            if len(product_variation) > 0:
                cart_item.variations.clear()
                for item in product_variation:
                    cart_item.variations.add(item)
            cart_item.save()

        return redirect('cart')



    # REMOVE SINGLE CART ITEM

def remove_cart(request, product_id, cart_item_id):
        # GET THE PRODUCT
    product = get_object_or_404(Product, id=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)

        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))

            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        
        # IF >1 ITEMS IN CART - REMOVE ONE
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        # OR DELETE last item
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')



# REMOVE MULTIPLE CART ITEMS

def remove_cart_item(request, product_id, cart_item_id):

    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product_id, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        product = get_object_or_404(Product, id=product_id )
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()

    
    return redirect('cart')




# CART VIEW

def cart(request, total=0, quantity=0, cart_items=None):
    # CHECK IF CART EXISTS - IF YES, GET CART ITEMS
    try:
        tax = 0
        grand_total = 0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        # ASSUMING 2% TAX - could make dynamic or configurable
        tax = (2 * total)/100
        #ADJUST TO 2 DECIMAL PLACES
        tax = round(tax, 2)
        grand_total = total + tax
        #ADJUST TO 2 DECIMAL PLACES
        grand_total = round(grand_total, 2)

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/cart.html', context)



@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0

        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total)/100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }

    return render(request, 'store/checkout.html', context)