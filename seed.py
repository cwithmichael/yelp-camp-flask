import random
from seed.seedhelpers import descriptors, places
from seed.cities import cities
from yelp.models import campground

sample = lambda array: array[random.randint(0, len(array)-1)]

def seed_db():
    camp = campground.Campground.objects.first()
    if camp:
        camp.drop_collection()
    for i in range(50):
        rando = random.randint(0, 1000)
        city = cities[rando]["city"]
        state = cities[rando]["state"]
        descriptor = sample(descriptors)
        place = sample(places)
        camp = campground.Campground(
            location=f"{city}, {state}",
            title=f"{descriptor} {place}",
            image="https://source.unsplash.com/collection/483251",
            description="This is a description.",
            price= (random.random() * 20) + 10,
        )
        camp.save()

if __name__=='__main__':
    seed_db()
