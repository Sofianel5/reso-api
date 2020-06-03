import datetime
from venues.models import TimeSlot

def dayH(startt, endt, interval, venuet, mt, type1="All"):
    counter = startt
    temp = 0
    while (counter < endt):
        temp = TimeSlot(venue =  venuet, start = counter, end = counter + datetime.timedelta(minutes = interval), max_attendees = mt, attendees = 0, type = type1)
        temp.save()
        print(temp)
        counter += datetime.timedelta(minutes = interval)

def test(test):
    print(test)



def day(magic, type="All"):
    dayH(magic[0], magic[1], magic[2], magic[3],magic[4],type)


def week(list):
    for i in list:
        day(i)


def main(args):
    day(args)

if __name__ == "__main__":
    main()
