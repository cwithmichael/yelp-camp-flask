from seedhelpers import descriptors, places
from cities import cities
import random
from mongoengine import connect, disconnect
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from yelp.models import campground
connect(host='mongodb+srv://cwithmichael:<password>@cluster0.jfeux.mongodb.net/<dbname>?retryWrites=true&w=majority', alias='money')

sample = lambda array: array[random.randint(0, len(array)-1)]
def seed_db():
    for i in range(50):
        rando = random.randint(0, 1000)
        city = cities[rando]["city"]
        state = cities[rando]["state"]
        descriptor = sample(descriptors)
        place = sample(places)
        camp = campground.Campground(
            location=f"{city}, {state}",
            title=f"{descriptor} {place}"
        )
        camp.save()

if __name__=='__main__':
    seed_db()
    disconnect(alias='money')


