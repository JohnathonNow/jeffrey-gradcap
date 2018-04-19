#!/usr/bin/env python

import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../..'))
import requests
import json
from PIL import Image
import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions

MAX_POWER = 2000

# Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'regular'  # If you have an Adafruit HAT: 'adafruit-hat'

matrix = RGBMatrix(options = options)

image = Image.new("RGB", (32, 32))
pixels = image.load()

#scale for converting RGB channel totals to amperes
scale = 4000.0/(255*32*32*3)

def hex2rgb(h):
    try:
        h=h.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2 ,4))
    except:
        return (0, 0, 0)


def read(v):
    #ask the server what's up
    r = requests.get('http://gradcap.us/read?v={}'.format(v))
    p = json.loads(r.text)
    #if our read was successful, let's do some stuff
    if p['status'] == 'success':
        #first make sure we got a new version
        if v < p['payload']['v']:
            #if so, we should change the matrix image as well as calculate the total current draw
            total = 0
            for i in range(0, 1024):
                #convert the color to a tuple
                c = hex2rgb(p['payload']['colors'][i])
                #set the pixel
                pixels[31-(i%32), 31-int(i/32)] = c
                #add to the total current
                total += sum(c)

            #if we exceeding the max current we are comfortable with
            if total*scale > MAX_POWER:
                #rescale the entire image
                rescale = MAX_POWER/(total*scale)
                for i in range(0, 1024):
                    pixels[31-(i%32), 31-int(i/32)] = tuple([int(x*rescale) for x in pixels[31-(i%32), 31-int(i/32)]])
        #update our version number
        v = p['payload']['v'];
        #refresh the matrix
        matrix.SetImage(image)
    return v

if __name__ == '__main__':
    v = 0;
    while 1:
        try:
            v = read(v)
            time.sleep(1)
        except:
            print("\b\bOK BYE")
            break
    matrix.Clear()
