import urllib2
import json
import Queue
import indicoio
from firebase import firebase
from random import shuffle
from twitter import *
#from firebase import firebase
from newspaper import Article

firebase = firebase.FirebaseApplication('https://in-the-loop.firebaseio.com', None)
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
'''
config = {}
execfile("config.py", config)

twitter = Twitter(auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))

results = twitter.trends.place(_id = 23424775)
'''
'''
Initializing firebase
'''
'''
firebase = firebase.FirebaseApplication('https://in-the-loop.firebaseio.com', None)
'''
'''
Initializing indico.io
'''
indicoio.config.api_key = '4d5aca20b4ea5a85a667de57c23d2e50'


'''
Main program
'''

#for location in results:
#    for trend in location["trends"]:
        #keyword = trend["name"]
keyword = "Paris Attacks"
allKeyWords = []
allKeyWordsCounts = []
allParagraphs = []
tags = []
adjKP = [[False for i in range(1000)] for j in range(1000)] # rows are paragraphs, columns are keywords
if keyword != None:
    if keyword[0] == '#':
        keyword = keyword[1:]
    # process keyword
    print "Results for " + keyword
    results = searchKeyword(keyword.replace(" ","+"), 15, 0)
    results += searchKeyword(keyword.replace(" ","+"), 15, 16)
    for x in range(len(results)):
        print results[x]["Url"]
        article = Article(results[x]["Url"])
        article.download()
        article.parse()
        paragraphs = article.text.split('\n')
        for p in paragraphs:
            if p.strip() == '' or len(p) < 280 or p.count('photo') > 4 or p.count('galler') > 4:
                continue
            i = 0
            keyWords = indicoio.keywords(p)
            if p in allParagraphs:
                i = allParagraphs.index(p)
            else:
                allParagraphs.append(p)
                tags.append((article.title, article.url))
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
    data = {
        'description': allParagraphs[res[0]].encode('utf-8').strip(),
        'header' : tags[res[0]][0],
        'tag': keyword,
        'image': 'http://lorempixel.com/1280/720/sporpyts/4/',
        'data' : []
    }
    for i in res:
        data['data'].append({
            'content':  allParagraphs[i].encode('utf-8').strip(),
            'type': 'paragraph',
            'source': {
                'name': 'Source',
                'url': tags[i][1]
            }
        })
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

        #firebase.post('/users', results[x]["Url"])
