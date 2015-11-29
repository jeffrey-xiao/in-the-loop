import urllib2
import json
import Queue
import indicoio
from firebase import firebase
from random import shuffle
from twitter import *
from newspaper import Article
import wolframalpha
import simplejson
import os
import sys
import struct
import imghdr
import time
from BeautifulSoup import BeautifulSoup
from googleplaces import GooglePlaces, types, lang
GOOGLE_PLACES_API_KEY = 'AIzaSyDFbP7p8fYhObGu5RuCrj5ynnwZ9yYWgtI'
google_places = GooglePlaces(GOOGLE_PLACES_API_KEY)
wolframClient = wolframalpha.Client('WY8W73-T5845VUK2Q')
'''
Max matching algorithm to determine optimal selection of paragraphs
'''
prev = []
v = []
def getMatching (N, M, adj):
    global prev, v
    prev = [-1]*M
    res = []
    for i in range(N):
        v = [False]*M
        if match(i, N, M, adj):
            res += [i]
    return res
def match (i, N, M, adj):
    for j in range(M):
        if adj[i][j] and not v[j]:
            v[j] = True
            if prev[j] == -1 or match(prev[j], N, M, adj):
                prev[j] = i
                return True
    return False

'''
Aho-corasick algorithm -- unused
'''
filein = open("words.txt", "r")
class Node:
    def __init__ (self, depth, index):
        self.depth = depth
        self.index = index
        self.child = [None]*128
        self.c = []
        self.isEnd = False
        self.fall = None
        self.parent = None
    def addWord (self, s):
        if self.depth == len(s):
            self.isEnd = True
            return
        curr = s[self.depth]
        index = ord(curr)
        if self.child[index] == None:
            self.child[index] = Node(self.depth + 1, index)
            self.child[index].parent = self
            self.c += [index]
        self.child[index].addWord(s)

def computeFall ():
    q = Queue.Queue()
    root.fall = root
    q.put(root)
    while not q.empty():
        curr = q.get()
        for i in curr.c:
            q.put(curr.child[i])
        if curr.fall != None:
            continue
        fall = curr.parent.fall
        while fall.child[curr.index] == None and fall != root:
            fall = fall.fall
        curr.fall = fall.child[curr.index]
        if curr.fall == None or curr.fall == curr:
            curr.fall = root

def printWord (n):
    if n != root:
        return printWord(n.parent) + chr(n.index)
    return ""

def searchDictionary (s):
    ret = []
    currState = root
    for i in range(len(s)):
        curr = s[i]
        index = ord(curr)
        while currState.child[index] == None and currState != root:
            currState = currState.fall
        if currState == root:
            if currState.child[index] != None:
                currState = currState.child[index]
        else:
            currState = currState.child[index]

        other = currState
        while other != root:
            if other.isEnd:
                ret += [str(printWord(other))]
            other = other.fall
    return ret

root = Node(0, 0)
root.parent = root;

def init ():
    for word in filein:
        root.addWord(word.lower().strip())
    computeFall()

'''
Initializing bing search api
'''

keyBing = 'w9Wv9QcXG2TrFgSdVdXNlcdDioOzGBmlNFhlu4994qk'
credentialBing = 'Basic ' + (':%s' % keyBing).encode('base64')[:-1] # the "-1" is to remove the trailing "\n" which encode adds

def searchKeyword (keyword, top, offset):
    url = 'https://api.datamarket.azure.com/Bing/Search/News?' + \
      'Query=%s&$top=%d&$skip=%d&$format=json' % ("%27"+keyword+"%27", top, offset)
    request = urllib2.Request(url)
    request.add_header('Authorization', credentialBing)
    requestOpener = urllib2.build_opener()
    response = requestOpener.open(request)

    return json.load(response)['d']['results']

'''
Initializing twitter
'''

config = {}
execfile("config.py", config)

twitter = Twitter(auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))

results = twitter.trends.place(_id = 9807)

'''
Initializing firebase
'''

firebase = firebase.FirebaseApplication('https://in-the-loop.firebaseio.com', None)

'''
Initializing indico.io
'''
indicoio.config.api_key = '4d5aca20b4ea5a85a667de57c23d2e50'


'''
Main program
'''

for location in results:
    for trend in location["trends"]:
#for z in range(1):
    #for trend in ["UFCSeoul", "Paris Attack", "Malta"]:
        keyword = trend["name"]
        #keyword =trend
        allKeyWords = []
        allKeyWordsCounts = []
        allParagraphs = []
        tags = []
        places = []
        adjKP = [[False for i in range(1000)] for j in range(1000)] # rows are paragraphs, columns are keywords
        imgContent = []
        if keyword != None:
            if keyword[0] == '#':
                keyword = keyword[1:]
            # process keyword
            print "Results for " + keyword
            results = searchKeyword(keyword.replace(" ","+"), 15, 0)
            if len(results) == 15:
                results += searchKeyword(keyword.replace(" ","+"), 15, 16)
            for x in range(len(results)):
                print results[x]["Url"]
                article = None
                try:
                    article = Article(results[x]["Url"])
                    article.download()
                    article.parse()
                except:
                    print "Could not parse HTML file"
                    continue
                if article.text.strip() == '' or 'embed.scribblelive' in article.html:
                    continue


                def get_image_size(fname):
                    '''Determine the image type of fhandle and return its size.
                    from draco'''
                    ext = 'png'
                    with open(fname, 'rb') as fhandle:
                        head = fhandle.read(24)
                        if len(head) != 24:
                            return
                        if imghdr.what(fname) == 'png':
                            check = struct.unpack('>i', head[4:8])[0]
                            if check != 0x0d0a1a0a:
                                return
                            width, height = struct.unpack('>ii', head[16:24])
                        elif imghdr.what(fname) == 'gif':
                            ext = 'gif'
                            width, height = struct.unpack('<HH', head[6:10])
                        elif imghdr.what(fname) == 'jpeg':
                            try:
                                fhandle.seek(0) # Read 0xff next
                                size = 2
                                ftype = 0
                                while not 0xc0 <= ftype <= 0xcf:
                                    fhandle.seek(size, 1)
                                    byte = fhandle.read(1)
                                    while ord(byte) == 0xff:
                                        byte = fhandle.read(1)
                                    ftype = ord(byte)
                                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                                # We are at a SOFn block
                                fhandle.seek(1, 1)  # Skip `precision' byte.
                                height, width = struct.unpack('>HH', fhandle.read(4))
                                ext = 'jpeg'
                            except Exception: #IGNORE:W0703
                                return
                        else:
                            return
                        return width, height, ext


                def get_images(URL):
                    default_dir = "/usr/share/nginx/html/img/uploads"
                    opener = urllib2.build_opener()
                    urllib2.install_opener(opener)
                    soup = BeautifulSoup(urllib2.urlopen(URL).read())
                    [x.extract() for x in soup.findAll('a')] #remove all links (including ads!!)
                    imgs = soup.findAll("img",{"alt":True, "src":True})
                    i = 0
                    for img in imgs:
                        img_url = img["src"]
                        if 'logo' in img_url:
                            continue
                        alt = img.get("alt","")
                        if img_url[:4] == "http":
                            name = str(time.time()) + str(i);
                            filename = os.path.join(default_dir, name)
                            i+=1
                            img_data = opener.open(img_url)
                            f = open(filename,"wb")
                            f.write(img_data.read())
                            f.close()
                            size = get_image_size(filename)
                            os.rename(filename, filename + size[2])
                            name += size[2]
                            filename = os.path.join(default_dir, name)

                            if size[0] < 200 or size[1] < 150:
                                os.remove(filename)
                            else:
                                info = {
                                    "image": name,
                                    "caption": alt,
                                    "src":    img_url,
                                    "date": article.publish_date,
                                    "source": URL
                                }
                                imgContent.append(info)
                    return

                try:
                    get_images(results[x]["Url"])
                    print "Image load success!"
                except:
                    print "Image load failed"

                entities = indicoio.named_entities(article.text)
                for key, value in entities.iteritems():
                    if value['categories']['location'] > 0.7:
                        key = key.lower()
                        if key not in places:
                            places.append(key)
                paragraphs = article.text.split('\n')
                for p in paragraphs:
                    if p.strip() == '' or len(p) < 280 or p.count('photo') > 4 or p.count('galler') > 4 or len(p) > 2500:
                        continue
                    i = 0
                    keyWords = indicoio.keywords(p)
                    if p in allParagraphs:
                        i = allParagraphs.index(p)
                    else:
                        allParagraphs.append(p)
                        tags.append((article.title, article.url, article.publish_date))
                        i = len(allParagraphs)-1
                    for keyWord in keyWords:
                        if keyWord in allKeyWords:
                            idx = allKeyWords.index(keyWord)
                            allKeyWordsCounts[idx] += 1
                            adjKP[i][idx] = True
                        else:
                            allKeyWords.append(keyWord)
                            allKeyWordsCounts.append(1)
                            adjKP[i][len(allKeyWords)-1] = True
            print allKeyWords
            pairs = []
            for i in range(0, len(allKeyWords)):
                pairs.append([allKeyWordsCounts[i], i])
            sorted(pairs)
            for i in range(0, len(pairs)):
                if i > 20:
                    for j in range(0, len(allParagraphs)):
                        adjKP[j][pairs[i][1]] = False
            res = getMatching(len(allParagraphs), len(allKeyWords), adjKP)
            print res
            description = "No relevant articles found."
            tag = "No relevant header found"
            if len(res) > 0:
                description = allParagraphs[res[0]].encode('utf-8').strip()
                tag = tags[res[0]][0]
            data = {
                'description': description,
                'header' : tag,
                'tag': keyword,
                'image': 'http://lorempixel.com/1280/720/sports/4/',
                'data' : [],
                'locations' : []
            }
            if len(imgContent) > 0:
                data['image'] = imgContent[0]['image']
            print places
            kk = 0
            for search in places:
                kk+=1
                if kk > 4:
                    break
                print ":"
                print search
                print ":"
                try:
                    query_result = google_places.nearby_search(location=search)
                    for place in query_result.places:

                        place.get_details()
                        if 'neighborhood' in place.details['types'] or 'locality' in place.details['types']:
                            wolfRes = wolframClient.query(search)
                            photos = None
                            if 'photos' in place.details:
                                photos = place.details['photos']
                            loc = {
                                'name': place.details['formatted_address'],
                                'photo': photos,
                                'description': [],
                                'lat': place.details['geometry']['location']['lat'],
                                'lon': place.details['geometry']['location']['lng']
                            }
                            for pod in wolfRes.pods:
                                loc['description'].append(pod.main.text)
                            data['locations'].append(loc)
                        break
                except:
                    print "Cannot parse location"

            political_sum = {
                'Libertarian':0.0,
                'Liberal':0.0,
                'Green':0.0,
                'Conservative':0.0
            }
            mood_avg = 0
            imageI = 0
            imgContent.sort(key=lambda x: (0 if x.caption.strip() == '' else 1), reverse=True)
            for i in res:
                political_sentiment = indicoio.political(allParagraphs[i].encode('utf-8').strip())
                mood = indicoio.sentiment(allParagraphs[i].encode('utf-8').strip())
                data['data'].append({
                    'content':  allParagraphs[i].encode('utf-8').strip(),
                    'type': 'paragraph',
                    'political-sentiment' : political_sentiment,
                    'mood' : mood,
                    'date' : tags[i][2],
                    'source': {
                        'name': 'Source',
                        'url': tags[i][1]
                    }
                })
                if imageI < len(imgContent):
                    data['data'].append({
                        'content': imgContent[imageI]['image'],
                        'type': 'image',
                        'date': imgContent[imageI]['date'],
                        'source': {
                            'name': 'Source',
                            'url': imgContent[imageI]['source']
                        },
                        'caption': imgContent[imageI]['caption']
                    })
                    imageI+=1

                print "date",tags[i][2]
                # 0 : libertarian; 1 : liberal; 2 : green; 3 : conservative
                for j in political_sentiment:
                    political_sum[j] += political_sentiment[j]
                mood_avg += mood
            if len(res) > 0:
                mood_avg /= len(res)
            data['political-sum'] = political_sum
            data['mood-avg'] = mood_avg
            result = firebase.post('/', data)

'''
nameEntities = indicoio.named_entities(article.text)
keyWords = indicoio.keywords(article.text)
paragraphs = article.text.split('\n')
ans = (0, "")

for p in paragraphs:
    res = 0.0
    for word in p.split():
        for keyWord in keyWords:
            if word == keyWord:
                res += keyWords[word]
        for nameEntity in nameEntities:
            if word == nameEntity:
                res += nameEntities[word]['confidence']
    if res > ans[0]:
        ans = (res, p)
print ans[1]
'''
