from django.shortcuts import render
from users.models import Account
from django.http import JsonResponse
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.utils.translation import gettext_lazy as _
from .models import HandshakeRequestFromVenue
from users.models import PeerToVenueHandshake
from venues.models import Venue
from datetime import datetime, timedelta
import uuid
from rest_framework.parsers import JSONParser
from .serializers import VenueSerializer
from .serializers import * 
from geolocation.utils import * 
from rest_framework.permissions import *
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from geolocation.models import Coordinates, Address
from .utils import get_coordinates, supported_version, update_location
from pytz import timezone
import dateutil.parser
import pytz

class VenueList(APIView):
    """
    List all venues, or create a new venue.
    """
    def get(self, request, format=None):
        if "page" in request.GET:
            page = int(request.GET["page"])
        else:
            page = 1 
        if "n" in request.GET:
            n = int(request.GET["n"])
        else:
            n = 12
        venues = Venue.objects.all()
        user_coordinates = get_coordinates(request)
        _sorted = sorted(venues, key= lambda v: v.coordinates.distance(user_coordinates))[(page-1)*n:+page*n]
        serializer = VenueSerializer(_sorted, many=True)
        return Response(serializer.data)

class VenueDetail(APIView):
    def get_object(self, pk):
        try:
            return Venue.objects.get(pk=pk)
        except:
            raise Http404
    def get(self, request, pk):
        venue = self.get_object(pk)
        serializer = VenueDetailSerializer(venue)
        return Response(serializer.data)

class TimeSlotManager(APIView):
    def get(self, request, pk):
        venue = Venue.objects.get(pk=pk)
        time_slots = venue.time_slots.all()
        coordinates = get_coordinates(request)
        local = timezone(coordinates.to_timezone())
        utc = pytz.utc
        now = utc.localize(datetime.now()).astimezone(local)
        available_slots = []
        for time_slot in time_slots:
            time_slot.start = utc.localize(time_slot.start).astimezone(local)
            time_slot.stop = utc.localize(time_slot.stop).astimezone(local)
            if time_slot.stop > now:
                available_slots.append(time_slot)
        serializer = TimeSlotSerializer(available_slots, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        venue = Venue.objects.get(pk=pk)
        try:
            assert(request.user == venue.admin)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        params = request.POST
        utc = pytz.utc 
        local = timezone(get_coordinates(request).to_timezone())
        params['start'] = dateutil.parser.parse(params['start'])
        params['stop'] = dateutil.parser.parse(params['stop'])
        params['start'] = local.normalize(local.localize(params['start']))
        params['stop'] = local.normalize(local.localize(params['stop']))
        params['start'] = params['start'].astimezone(utc)
        params['stop'] = params['stop'].astimezone(utc)
        params['venue'] = venue
        time_slot = TimeSlot.objects.create(params, save=False)
        time_slot.venue = venue
        time_slot.save()

class TimeSlotRegistration(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, venue, timeslot):
        venue = Venue.objects.get(pk=venue)
        timeslot = TimeSlot.objects.get(pk=timeslot)
        user = request.user 
        try:
            assert(timeslot in venue.time_slots.all())
            timeslot.add_attendee(user)
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    
    def get(self, request, venue, timeslot):
        venue = Venue.objects.get(pk=venue)
        timeslot = TimeSlot.objects.get(pk=timeslot)
        user = request.user 
        if user not in timeslot.attendees.all():
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        
class VenueSearch(APIView):
    def get(self, request):
        q = request.GET['q']
        types = Venue.objects.filter(type__contains=q)
        descs = Venue.objects.filter(description__contains=q)
        titles = Venue.objects.filter(title__contains=q)
        union = types.union(descs).union(titles)
        user_coordinates = get_coordinates(request)
        _sorted = sorted(union, key= lambda v: v.coordinates.distance(user_coordinates))
        serializer = VenueSerializer(union, many=True)
        return Response(serializer.data)


class CustomUserUpdate(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if not supported_version(request):
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        user = request.user
        coordinates = get_coordinates(request)
        if user.coordinates != coordinates:
            update_location(user, coordinates)
        user_serializer = InternalAccountSerializer(user)
        return Response(user_serializer.data)

class ToggleLockState(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user 
        user.is_locked = not user.is_locked
        user.save()
        return Response({"is_locked": user.is_locked}, status=status.HTTP_200_OK) 

class UserScanManager(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        requests = HandshakeRequestFromVenue.objects.filter(_to=user, time__gte=(datetime.now()-timedelta(minutes=5)))
        if requests.count() > 0:
            _request = requests[len(requests)-1]
            thread = HandshakeRequestFromVenueSerializer(instance=_request).data 
            thread["success"] = True
            return JsonResponse(thread, safe=False)
        else:
            return JsonResponse({"success": False, "message": _("You haven't been scanned yet.")}, safe=False, status=status.HTTP_404_NOT_FOUND)
    def post(self, request):
        user = request.user
        thread = HandshakeRequestFromVenue.objects.get(pk=request.POST["thread"])
        thread.confirm()
        return Response(status=status.HTTP_200_OK)

class VenueScanManager(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        user = request.user
        venue = Venue.objects.get(pk=pk)
        to = Account.objects.get(public_id=uuid.UUID(request.POST["to"]))
        try:
            assert(not to.is_locked)
        except:
            return Response(status=status.HTTP_417_EXPECTATION_FAILED)
        try:
            assert(venue.admin == user)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        registered = False
        timeslots = venue.get_current_timeslots()
        for timeslot in timeslots:
            if to in timeslot.attendees.all():
                registered = True 
        try:
            assert(registered)
        except:
            return Response(status=status.HTTP_412_PRECONDITION_FAILED)
        hs = HandshakeRequestFromVenue.objects.create(_from=venue, _to=to)
        serializer = HandshakeRequestFromVenueSerializer(hs)
        return Response(serializer.data)

class UserBookingsManager(APIView):
    def get(self, request):
        ts = request.user.time_slots.all()
        history = []
        current = []
        for t in ts:
            if t.past:
                history.append(t)
            else:
                current.append(t)
        res = {
            "history": TimeSlotSerializer(history, many=True).data,
            "current": TimeSlotSerializer(current, many=True).data,
        }
        return Response(res)

class VenueAdminLogin(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if (request.user.venues.count() != 0):
            serialized = dict(VenueAdminSerializer(user).data)
            serialized["venue"] = serialized["venues"][0]
            return Response(serialized)
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

class VenueAdminTimeSlotInfo(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, venue):
        user = request.user
        venue = Venue.objects.get(pk=pk)
        try:
            assert(venue.admin == user)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        history = TimeSlots.objects.filter(venue=venue, past=True)
        current = TimeSlots.objects.filter(venue=venue, past=False)
        res = {
            "history": TimeSlotSerializer(history, many=True).data,
            "current": TimeSlotSerializer(current, many=True).data,
        }
        return Response(res)
        
class Fixture(APIView):
    def get(self, request):
        if request.GET["type"] == "thread":
            record = HandshakeRequestFromVenue.objects.all()[0]
            serializer = HandshakeRequestFromVenueSerializer(record)
        if "venue" in request.GET["type"]:
            record = Venue.objects.all()[0]
            if request.GET["type"] == "venue":
                serializer = VenueSerializer(record)
            if request.GET["type"] == "venue_small":
                serializer = VenueSerializer(record)
            if request.GET["type"] == "venue_detail":
                serializer = VenueDetailSerializer(record)
        if "user" in request.GET["type"]:
            record = Account.objects.all()[0]
            if request.GET["type"] == "user_signup":
                serializer = UserRegistrationSerializer(record)
            if request.GET["type"] == "user_external":
                serializer = ExternalAccountSerializer(record)
            if request.GET["type"] == "user_internal":
                serializer = InternalAccountSerializer(record)
        if request.GET["type"] == "handshake":
            record = PeerToVenueHandshake.objects.all()[0]
            serializer = PeerToVenueHandshakeSerializer(record)
        if request.GET["type"] == "timeslot":
            record = TimeSlot.objects.all()[0]
            serializer = TimeSlotSerializer(record)
        if request.GET["type"] == "address":
            record = Address.objects.all()[0]
            serializer = AddressSerializer(record)
        if request.GET["type"] == "coordinates":
            record = Coordinates.objects.all()[0]
            serializer = CoordinatesSerializer(record)
        return Response(serializer.data)






