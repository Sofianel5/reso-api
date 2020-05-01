from geolocation.models import Coordinates, Address
from geolocation.utils import getCoordinatesFromRequest

class Config():
    DEFAULT_VENUES_PER_REQ = 20 
    DEFAULT_COORDS = {'lat': 40.712776, 'lng': -74.005974}

def get_coordinates(request, fieldname="coordinates"):
    try:
        lat, lng = (request.META['HTTP_LAT'], request.META["HTTP_LNG"])
        coords, _ = Coordinates.objects.get_or_create(lat=lat, lng=lng)
        return coords
    except Exception as e:
        print(e)
        print("unable to parse")
        try:
            return getCoordinatesFromRequest(request)
        except:
            print("using default coordinates")
            coords, _ = Coordinates.objects.get_or_create(lat=Config.DEFAULT_COORDS['lat'], lng=Config.DEFAULT_COORDS['lng'])
            print(coords)
            return coords
def _get_coordinates(request, fieldname="coordinates"):
    print(request.META)
    lat, lng = (request.META['HTTP_LAT'], request.META["HTTP_LNG"])
    coords, _ = Coordinates.objects.get_or_create(lat=lat, lng=lng)
    print(coords)
    return coords

def update_location(user, coordinates):
    user.coordinates = coordinates 
    user.address = coordinates.to_address()
    user.save()
    return user