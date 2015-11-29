import googlemaps

gmaps = googlemaps.Client(key = "")

res = gmaps.geocode("Paris")
print res[0]['geometry']['location']['lat'],res[0]['geometry']['location']['lng']
print gmaps.reverse_geocode((res[0]['geometry']['location']['lat'], res[0]['geometry']['location']['lng']))
