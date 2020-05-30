from django import forms
from users.models import *
from venues.models import *
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autocomplete':'off'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': "First name", 'required':'required'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': "Last name", 'required':'required'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': "Last name", 'required':'required'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder': "Last name", 'required':'required'}))
    class Meta:
        model = Account
        fields = ['first_name', 'last_name' 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        name = self.cleaned_data.get('name')
        if email and Account.objects.filter(email=email).exclude(name=name).exists():
            raise forms.ValidationError(u'Email addresses must be unique.')
        return email

class VenueCreationForm(forms.ModelForm):
    class Meta:
        model = Venue