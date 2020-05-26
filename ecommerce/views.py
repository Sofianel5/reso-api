from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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