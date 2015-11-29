import googlemaps

gmaps = googlemaps.Client(key = "AIzaSyCx2OdZxrmvJwek2zGyIojR7auQnbRdQAg")

res = gmaps.geocode("Paris")
print res[0]['geometry']['location']['lat'],res[0]['geometry']['location']['lng']
print gmaps.reverse_geocode((res[0]['geometry']['location']['lat'], res[0]['geometry']['location']['lng']))