import datetime
from venues.models import TimeSlot

def generate_between_interval(startt, endt, interval, venuet, mt, type1="All"):
    counter = startt
    while (counter < endt):
        temp = TimeSlot.objects.create(venue=venuet, start=counter,stop=(counter + datetime.timedelta(minutes = interval)), max_attendees = mt, type = type1)
        temp.save()
        print(temp)
        counter += datetime.timedelta(minutes = interval)