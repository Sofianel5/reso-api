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
        context['form'] = CheckoutForm(request.POST)
        if context["form"].is_valid():
            ref_code = context['form'].cleaned_data.get("ref_code")
            try:
                cupon = Cupon.objects.get(code=context['form'].cleaned_data.get("cupon_code"))
            except Cupon.DoesNotExist:
                cupon = None
            address = Address.objects.create(
                address_1=context['form'].cleaned_data.get("billing_address")
                address_1=context['form'].cleaned_data.get("billing_address2")
                city=context['form'].cleaned_data.get("billing_city")
                state=context['form'].cleaned_data.get("billing_state")
            )
            order = Order.objects.create(
                user=request.user,
                ref_cod=ref_code,
                billing_address=address,
                # set transaction later
            )

    context.update({
        'subscription': subscription,
        'STRIPE_PUBLISHABLE_KEY': publickey
    })
    return render(request, "ecommerce/checkout.html", context)

@login_required
def pay(request):
    publickey = settings.STRIPE_PUBLISHABLE_KEY
    context = {
        'form': PaymentForm()
    }
    if request.method == "GET":
        subscription = SubscriptionType.objects.get(name=request.GET["name"])
    else:
        try:
            context['form'] = PaymentForm(request.POST)
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
        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.warning(request, f"{err.get('message')}")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(request, "Rate limit error")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            print(e)
            messages.warning(request, "Invalid parameters")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(request, "Not authenticated")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(request, "Network error")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(request, "Something went wrong. You were not charged. Please try again.")

        except Exception as e:
            # send an email to ourselves
            messages.warning(self.request, "A serious error occurred. We have been notifed.")
            send_mail(
                'Error in processing payment',
                'email: ' +request.user.email,
                'users@tracery.us',
                ['sofiane@tracery.us'],
                fail_silently=False,
            )
            db_logger.exception(e)

    context.update({
        'subscription': subscription,
        'STRIPE_PUBLISHABLE_KEY': publickey
    })
    return render(request, "ecommerce/pay.html", context)

def success(request):
    return render(request, "ecommerce/success.html")


