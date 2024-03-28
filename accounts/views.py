from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from orders.models import Order, OrderProduct

# EMAIL VERIFICATION
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


from django.urls import reverse
from django.http import HttpResponseRedirect

from carts.models import Cart, CartItem
from carts.views import _cart_id


import requests


# Create your views here.

def register(request):
    if request.method == 'POST':

        print('POST request received')
        form = RegistrationForm(request.POST)
        if form.is_valid():
            print('Form is valid')
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()

            # CREATE USER PROFILE
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/avatar1.jpg'
            profile.save()

            print('User created')
            
            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user.first_name,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            to_email = email 
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request, 'Thank you for registering with us. We have sent you an email to verify your account.')
            return HttpResponseRedirect(reverse('login') + '?command=verification&email=' + email)
            
    else:
        form = RegistrationForm()

    context = {
        'form': form,
    }

    return render(request, 'accounts/register.html', context)




def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        # check if user logged in
        if user is not None:
            try: 
                # get the cart using the cart_id present in the session
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # get the product variations by cart id
                    product_variation = []

                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))

                    # get the cart items from the user to access their cart
                        
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []

                    # GET EXISTING VARIATIONS
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    

                    # COMMONALITIES BETWEEN PRODUCT VARIATION AND EXISTING VARIATION
                    for pr in product_variation:
                        if pr in ex_var_list:
                            # get the index of that variation
                            index = ex_var_list.index(pr)
                            # get the id of the item with that variation
                            item_id = id[index]
                            # get the item with that id
                            item = CartItem.objects.get(id=item_id)
                            # add quantity of the item with the same variation
                            item.quantity += 1
                            # save the item with the new quantity for the user
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass

            auth.login(request, user)
            messages.success(request, 'You are now logged in')

            # IF LOGIN WAS PROMPTED BY PAGE REQUEST - REDIRECT TO PAGE
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
            
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
        
    return render(request, 'accounts/login.html')   




@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are now logged out')
    return redirect('login')



def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    # check if user and token is valid
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Account activated successfully')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')
    



@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    context = {
        'orders_count': orders_count,
    }
    return render(request, 'accounts/dashboard.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        # check if account exists
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            to_email = email 
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'Password reset email has been sent to your email address')
            return redirect('login')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')
        
    return render(request, 'accounts/forgot_password.html')



def resetpassword_validate(request, uidb64, token):
    # check if user is logged in
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    # check if user and token is valid
    if user is not None and default_token_generator.check_token(user, token):
        # set user in session
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has expired')
        return redirect('login')


def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            # get user from session
            uid = request.session.get('uid')
            # get user by id
            user = Account.objects.get(pk=uid)
            # set new password
            user.set_password(password)
            # save user
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('reset_password')
    else:
        return render(request, 'accounts/reset_password.html')
    
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='login')
def edit_profile(request):

    user_profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        # Get user instance of profile to update
        user_form = UserForm(request.POST, instance=request.user)
        # Get user profile instance of profile to update and files for profile picture
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile,
    }

    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            # check before proceeding
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()

                # auth.logout(request)
                messages.success(request, 'Password updated successfully')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter correct current password')
                return redirect('change_password')
        else:
            messages.error(request, 'Passwords do not match')
            return redirect('change_password')
        
    context = {}
    return render(request, 'accounts/change_password.html', context)


@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    individual_total = []

    for item in order_detail:
        subtotal += item.product_price * item.quantity
        total = item.product_price * item.quantity
        individual_total.append(total)

    ord_prods = zip(order_detail, individual_total)

    context = {
        'order': order,
        'order_detail': order_detail,
        'subtotal': subtotal,
        'ord_prods': ord_prods,
    }

    return render(request, 'accounts/order_detail.html', context)