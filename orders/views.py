from django.shortcuts import render, redirect
from .models import Payment, Order, OrderProduct
from carts.models import Cart, CartItem
from .forms import OrderForm
import datetime
from store.models import Product
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse




# Create your views here.

def payments(request):
    print("Payments view is called")
    body = json.loads(request.body)
    print(body)
    order = Order.objects.get(user=request.user, is_ordered = False, order_number= body['orderID'])

    # Store transaction details inside PAYMENT model
    payment = Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    # Update ORDER model 
    order.payment = payment
    order.is_ordered = True
    order.save()


    # Move the cart items to the Order Product table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.ordered = True
        # ManytoManyField needs to be saved first
        order_product.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()


    # Decrement the quantity of the available stock

    product = Product.objects.get(id=item.product_id)
    product.stock -= item.quantity
    product.save()

    # CLEAR the cart 
    
    CartItem.objects.filter(user=request.user).delete()

    # SEND order EMAIL to customer
    
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_received_email.html', {
        'user': request.user,
        'order': order,
    })

    to_email = request.user.email 
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # SEND order number and transaction id to sendData method via JSON1

    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id,
    }

    return JsonResponse(data)


def place_order(request, total=0, quantity=0):

    print("Place Order view is called")
    # fetch the cart and cart items
    current_user = request.user
    # if the cart count is less than or equal to 0, redirect to store
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    # INITIALIZE VARIABLES FOR TOTALS
    
    grand_total = 0
    tax = 0

    # CALCULATE TOTALS
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    tax = round(tax, 2)
    print("Tax: ", tax)
    grand_total = total + tax  
    # round to 2 decimal places
    grand_total = round(grand_total, 2)

    print("Grand Total: ", grand_total)
    # store billing information inside Order table
    if request.method == 'POST':
        print("POST request is received")
        form = OrderForm(request.POST)

        if form.is_valid():
            print("Form is valid")
            # store billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            
            data.save()

        
            # generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            mt = int(datetime.date.today().strftime('%m'))
            dt = int(datetime.date.today().strftime('%d'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y%m%d')

            order_number = current_date + str(data.id)  # 20210525
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            print("orders/payments is called")
            return render(request, 'orders/payments.html', context)
        
    else:
        print("LOAD CHECKOUT AFTER RENDERING PAYMENTS")
        return redirect('checkout')
        
    return redirect('store')



def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        individual_total = []

        for i in ordered_products:
            subtotal += i.product_price * i.quantity
            item = OrderProduct.objects.get(id=i.id)
            total = item.product_price * item.quantity
            individual_total.append(total)
      
        ord_prods = zip(ordered_products, individual_total)
        payment = Payment.objects.get(payment_id=transID)
    
        context = {
            'order': order,
            # 'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
            'ord_prods': ord_prods,
        }
        return render(request, 'orders/order_complete.html', context)

    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')