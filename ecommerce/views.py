from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *
import stripe
import tracery import settings

# Create your views here.
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
    return render(request, "ecommerce/signup.html", context)

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

