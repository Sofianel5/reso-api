from django import forms
from users.models import *
from venues.models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete':'off'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': "First name", 'required':'required'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': "Last name", 'required':'required'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': "Password", 'required':'required'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': "Password (confirm)", 'required':'required'}))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

class SignInForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete':'off', 'class':'form-control', 'placeholder': "Email"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': "Password", 'required':'required'}))

class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = (
        ('S', 'Stripe'),
    )
    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_state = forms.CharField(required=False)
    billing_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    billing_zip = forms.CharField(required=False)

    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)

class VenueCreationForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['type', 'description', 'title', 'address', 'phone', 'email']

