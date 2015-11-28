import urllib2
import os
import sys
import struct
import imghdr
from BeautifulSoup import BeautifulSoup

def get_image_size(fname):
    '''Determine the image type of fhandle and return its size.
    from draco'''
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
            except Exception: #IGNORE:W0703
                return
        else:
            return
        return width, height

def get_images(URL):
    default_dir = "LillianImages"
    opener = urllib2.build_opener()
    urllib2.install_opener(opener)
    soup = BeautifulSoup(urllib2.urlopen(URL).read())
    imgs = soup.findAll("img",{"alt":True, "src":True})

    for img in imgs:
        img_url = img["src"]
        alt = img.get("alt","")
        print alt
        if img_url[:4] == "http":
            filename = os.path.join(default_dir, img_url.split("/")[-1])
            img_data = opener.open(img_url)
            f = open(filename,"wb")
            f.write(img_data.read())
            f.close()
            size = get_image_size(filename)
            if size[0] < 200 or size[1] < 150:
                os.remove(filename)
    return
