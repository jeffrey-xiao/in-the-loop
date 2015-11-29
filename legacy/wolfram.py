import wolframalpha
import simplejson
from googleplaces import GooglePlaces, types, lang
GOOGLE_PLACES_API_KEY = ''
google_places = GooglePlaces(GOOGLE_PLACES_API_KEY)
wolframClient = wolframalpha.Client('')
places = ['Paris', 'Europe',  'Ontario', 'USA', '9 Havagal Crescent, Markham, Ontario']
locations = []
for search in places:
    query_result = google_places.nearby_search(
            location=search)
    for place in query_result.places:

        place.get_details()
        if 'neighborhood' in place.details['types'] or 'locality' in place.details['types']:
            res = wolframClient.query(search)
            location = {
                'name': place.details['formatted_address'],
                'photo': place.details['photos'],
                'description': [],
                'lat': place.details['geometry']['location']['lat'],
                'lon': place.details['geometry']['location']['lng']
            }
            for pod in res.pods:
                location['description'].append(pod.main.text)
            locations.append(location)
        break

'''
client = wolframalpha.Client('WY8W73-T5845VUK2Q')
place = "Paris"
res = client.query(place)
for pod in res.pods:
    print(pod.main)
'''
