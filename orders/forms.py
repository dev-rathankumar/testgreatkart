from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note']

        # widgets = {
        #     'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
        #     'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        #     'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
        #     'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        #     'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 1'}),
        #     'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address Line 2'}),
        #     'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
        #     'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
        #     'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
        #     'order_note': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Order Note'}),
        # }



        