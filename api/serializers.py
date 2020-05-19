from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from venues.models import Venue, TimeSlot
from users.models import Account, PeerToVenueHandshake
from .models import *
from geolocation.models import Coordinates, Address

class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('email', 'first_name', 'last_name', 'password')
    

class ExternalAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account 
        fields = ["id", "first_name", "last_name"]

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"

class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = "__all__"

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        exclude = ['admin']
        depth = 1

class TitleVenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ["id", "title"]

class PeerToVenueHandshakeSerializer(serializers.ModelSerializer):
    user = ExternalAccountSerializer()
    venue = TitleVenueSerializer()
    class Meta:
        model = PeerToVenueHandshake
        fields = "__all__"

class TimeSlotSerializer(serializers.ModelSerializer):
    venue = TitleVenueSerializer()
    class Meta:
        model = TimeSlot 
        fields = ['start', 'stop', 'max_attendees', 'num_attendees', 'id', 'current', 'past', 'venue', 'type']
        
class InfoTimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot 
        fields = ['start', 'stop', 'max_attendees', 'num_attendees', 'id', 'current', 'past', 'type']

class VenueDetailSerializer(serializers.ModelSerializer):
    admin = ExternalAccountSerializer()
    bookable_time_slots = InfoTimeSlotSerializer(many=True)
    #time_slots = TimeSlotSerializer(many=True)
    class Meta:
        model = Venue
        fields = "__all__"
        depth = 1

class InternalAccountSerializer(serializers.ModelSerializer):
    is_venueadmin = serializers.ReadOnlyField()
    class Meta:
        model = Account
        exclude = ["password", "is_staff", "last_login", "is_admin", "is_active"]
        depth = 2
        
class HandshakeRequestFromVenueSerializer(serializers.ModelSerializer):
    venue = TitleVenueSerializer()
    user = ExternalAccountSerializer()
    class Meta:
        model = HandshakeRequestFromVenue
        exclude = ["_from", "_to"]
        depth = 1

class VenueAdminSerializer(serializers.ModelSerializer):
    venues = VenueSerializer(many=True)
    class Meta:
        model = Account
        exclude = ["password", "is_staff", "last_login", "is_admin", "is_active"]
        depth = 2
