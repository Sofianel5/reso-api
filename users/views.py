from django.shortcuts import render
from .models import Account 

# Create your views here.

def user_preview(request):
    pk = request.GET["user"]
    user = Account.objects.get(pk=pk)
    assert(user.is_venueadmin)
    return render(request, "users/user_preview.html", {"user": user})
    
