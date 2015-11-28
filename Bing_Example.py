import urllib2
import json
from twitter import *

keyBing = 'w9Wv9QcXG2TrFgSdVdXNlcdDioOzGBmlNFhlu4994qk'
credentialBing = 'Basic ' + (':%s' % keyBing).encode('base64')[:-1] # the "-1" is to remove the trailing "\n" which encode adds
top = 10
offset = 0

def search (keyword):
    url = 'https://api.datamarket.azure.com/Bing/Search/News?' + \
      'Query=%s&$top=%d&$skip=%d&$format=json' % (keyword, top, offset)
    request = urllib2.Request(url)
    request.add_header('Authorization', credentialBing)
    requestOpener = urllib2.build_opener()
    response = requestOpener.open(request) 
    
    return json.load(response)['d']['results']

config = {}
execfile("config.py", config)

twitter = Twitter(auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))

results = twitter.trends.place(_id = 1)

for location in results:
    for trend in location["trends"]:
        print " - %s" % trend["name"]