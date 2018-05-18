#!/usr/bin/env python
#    This file is the raspberry pi client for the software on my graduation cap, Jeffrey-Gradcap.
#    Copyright (C) 2018 John Westhoff

#    This file is part of Jeffrey-Gradcap.
#
#    Jeffrey-Gradcap is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Jeffrey-Gradcap is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Jeffrey-Gradcap.  If not, see <http://www.gnu.org/licenses/>.

import os
import requests
import gol
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
options.hardware_mapping = 'regular'
options.gpio_slowdown = 1

matrix = RGBMatrix(options = options)

image = Image.new("RGB", (32, 32))
pixels = image.load()

ndlogo = Image.open("/home/pi/jeffrey-gradcap/ndlogo.png").convert("RGB")

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
        if p['payload']['mode'] == 1:
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

            #refresh the matrix
            matrix.SetImage(image)
        elif p['payload']['mode'] == 2:
            matrix.SetImage(ndlogo)
        elif p['payload']['mode'] == 3:
            e = gol.Ecosystem(32, 32) 
            e.seed()
            for i in range(0, 100):
                e.tick()
                for cell in e:
                    pixels[cell[0], cell[1]] = e.color(*cell)
                #refresh the matrix
                matrix.SetImage(image)
            p['payload']['v'] = 0
        elif p['payload']['mode'] == 0:
            os.system("sudo poweroff")
        else:
            #refresh the matrix
            matrix.SetImage(image)
        #update our version number
        v = p['payload']['v']
    return v

if __name__ == '__main__':
    v = 0;
    while 1:
        try:
            v = read(v)
            time.sleep(1)
        except KeyboardInterrupt:
            print("\b\bOK BYE")
            break
        except Exception as E:
            print(E)
            time.sleep(10)
    matrix.Clear()
