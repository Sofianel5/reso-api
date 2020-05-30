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
from django.core.mail import send_mail
from django.contrib import messages
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

def choose_subscription(request):
    context = {
        'types': SubscriptionType.objects.all()
    }
    return render(request, "ecommerce/pricing.html", context)

def team(request):
    return render(request, "ecommerce/our_team.html")

@login_required 
def enterprise(request):
    send_mail(
        'New enterprise request',
        'email: ' +request.user.email,
        'users@tracery.us',
        ['sofiane@tracery.us'],
        fail_silently=False,
    )
    context = {
        'user': request.user
    }
    return render(request, "ecommerce/enterprise.html", context)

@login_required 
def checkout(request):
    publickey = settings.STRIPE_PUBLISHABLE_KEY
    context = {
        'form': CheckoutForm()
    }
    if request.method == "GET":
        subscription = SubscriptionType.objects.get(name=request.GET["name"])
    else:
        try:
            context['form'] = CheckoutForm(request.POST)
            token = request.POST['stripeToken']
            subscription = SubscriptionType.objects.get(name=request.POST["name"])
            charge = stripe.Charge.create(
                amount=subscription.default_cost,
                currency='usd',
                description=str(subscription),
                source=token
            )
            subscriptionRecord = Subscription.objects.create(
                type=subscription,
                user=request.user,
                term_length=request.POST["term_length"]
            )
            transaction = Transaction.objects.create()
            return redirect(reverse('success'))
        except:
            context["failure"] = True
            return redirect(reverse('failure'))
    context.update({
        'subscription': subscription,
        'STRIPE_PUBLISHABLE_KEY': publickey
    })
    return render(request, "ecommerce/checkout.html", context)

def success(request):
    return render(request, "ecommerce/success.html")


