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
import dateutil.parser
import logging
from django.core.mail import send_mail
db_logger = logging.getLogger('db')

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
        available_slots = []
        now = datetime.now()
        for time_slot in time_slots:
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
        params = {}
        params['start'] = dateutil.parser.parse(request.POST.get('start'))
        params['stop'] = dateutil.parser.parse(request.POST.get('stop'))
        params["max_attendees"] = request.POST.get("max_attendees")
        params['venue'] = venue
        time_slot = TimeSlot.objects.create(start=params['start'], stop=params['stop'], max_attendees=params["max_attendees"], venue=params['venue'])
        time_slot.save()
        return Response(status=status.HTTP_200_OK)

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
        timeslots = venue.current_timeslots()
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
    def get(self, request, pk):
        user = request.user
        venue = Venue.objects.get(pk=pk)
        try:
            assert(venue.admin == user)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ts = venue.time_slots.all()
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
    
class DeleteTimeSlot(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk, timeslotId):
        user = request.user
        venue = Venue.objects.get(pk=pk)
        try:
            assert(venue.admin == user)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        timeslot = TimeSlot.objects.get(pk=timeslotId)
        timeslot.delete()
        return Response(status=status.HTTP_200_OK)
    
class VenueContact(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        user = request.user
        venue = Venue.objects.get(pk=pk)
        try:
            assert(venue.admin == user)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        send_mail(
            'New support request',
            'email: ' +request.user.email + "<br>" + request.POST["content"],
            'users@tracery.us',
            ['sofiane@tracery.us'],
            fail_silently=False,
        )
        return Response(status=status.HTTP_200_OK)

class ExternalAttendeeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, venueid, timeslotid):
        user = request.user
        venue = Venue.objects.get(pk=venueid)
        timeslot = TimeSlot.objects.get(pk=timeslotid)
        try:
            assert(venue.admin == user)
            assert(timeslot.venue == venue)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            if request.POST["add"]:
                timeslot.add_external_attendee()
            else:
                timeslot.remove_external_attendee()
        except Exception as e:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE) 
        
class AttendanceIncrement(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, venueid):
        user = request.user
        venue = Venue.objects.get(pk=venueid)
        timeslot = venue.current_timeslot()
        try:
            assert(venue.admin == user)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        timeslot.record_attending(request.POST["count"])
        return Response({"attendees": timeslot.attending})

class ClearAttendees(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, venueid):
        user = request.user
        venue = Venue.objects.get(pk=venueid)
        timeslot = venue.current_timeslot()
        try:
            assert(venue.admin == user)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        timeslot.clear_attendees()
        serializer = TimeSlotSerializer(timeslot)
        return Response(serializer.data)