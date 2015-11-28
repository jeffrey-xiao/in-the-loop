import urllib2
import os
import sys
from BeautifulSoup import BeautifulSoup
URL = sys.argv[1]
default_dir = "LillianImages"
opener = urllib2.build_opener()
urllib2.install_opener(opener)
soup = BeautifulSoup(urllib2.urlopen(URL).read())
imgs = soup.findAll("img",{"alt":True, "src":True})
for img in imgs:
    img_url = img["src"]
    if img_url[:4] == "http":
        filename = os.path.join(default_dir, img_url.split("/")[-1])
        img_data = opener.open(img_url)
        f = open(filename,"wb")
        f.write(img_data.read())
        f.close()
