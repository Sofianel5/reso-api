from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import *
from .forms import *
import stripe
from django.contrib.auth import login
from tracery import settings
import logging
db_logger = logging.getLogger('db')
stripe.api_key = settings.STRIPE_SECRET_KEY

def home(request):
    return render(request, "ecommerce/homepage.html")

def signup(request):
    context = {}
    if request.method == "GET":
        context["form"] = UserRegisterForm()
    else:
        form = UserRegisterForm(request.POST)
        context["form"] = form
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return HttpResponseRedirect(reverse('home')) # redirect to success: sell or buy
        else:
            db_logger.info(form.errors)
    return render(request, "ecommerce/signup.html", context)

def pricing(request):
    return render(request, "ecommerce/pricing.html")

def subscribe(request):
    return render(request, "ecommerce/checkout.html")

@login_required
def choose_subscription(request):
    return render(request, "ecommerce/subscriptions.html")

@login_required 
def checkout(request):
    publickey = settings.STRIPE_PUBLISHABLE_KEY
    context = {}
    if request.method == "GET":
        subscription = SubscriptionType.objects.get(pk=request.GET["type"])
    else:
        try:
            token = request.POST['stripeToken']
            subscription = SubscriptionType.objects.get(pk=request.POST["type"])
            charge = stripe.Charge.create(
                amount=subscription.cost,
                currency='usd',
                description=str(subscription),
                source=token
            )
            return redirect(reverse('success'))
        except:
            context["failure"] = True
            return redirect(reverse('failure'))
    context.update({
        'subscription': subscription,
        'STRIPE_PUBLISHABLE_KEY': publickey
    })
    return render(request, "ecommerce/checkout.html", context)

