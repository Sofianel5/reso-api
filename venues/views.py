from django.shortcuts import render
from .models import Venue 

# Create your views here.
def venue_preview(request):
    pk = request.GET["venue"]
    venue = Venue.objects.get(pk=pk)
    return render(request, "venues/venue_preview.html", {"venue": venue})