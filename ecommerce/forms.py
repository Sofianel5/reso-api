from django import forms
from users.models import *
from venues.models import *
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete':'off'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': "First name", 'required':'required'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': "Last name", 'required':'required'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': "Password", 'required':'required'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': "Password (confirm)", 'required':'required'}))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

class VenueCreationForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['type', 'description', 'title', 'address', 'phone', 'email']