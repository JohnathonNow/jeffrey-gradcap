#!/usr/bin/env python3
import cherrypy
from cherrypy.lib import static
import os
import urllib
import json
import threading
import time
from datetime import datetime
import signal

TIMEOUT = 30 #timeout for requests, for long polling
SIZE = 32*32 #number of pixels

data = {}
#initialize grid to all black
data['colors'] = ['#000000' for x in range(0, SIZE)]
#keep track of a "version number" for detecting changes
data['v'] = 1
#modes, 0 = power off pi, 1 = show ND logo, 2 = game of life
data['mode'] = 1
#log changes to output file
output = None
#a lock for thread safety
lock = threading.Lock()

def usr1():
    lock.acquire()
    data['mode'] = 0
    lock.release()

def usr2():
    lock.acquire()
    if data['mode'] == 1:
        data['mode'] = 2
    elif data['mode'] == 2:
        data['mode'] = 1
    lock.release()

signal.signal(signal.SIGUSR1, usr1)
signal.signal(signal.SIGUSR2, usr2)

class Page(object):
    @cherrypy.expose
    def read(self, v):
        ct = datetime.now() #get the start time, for long polling
        response = {'status': 'success', 'v': '9999999'}
        try:
            lock.acquire()
            while int(v) >= int(data['v']): #wait for new data
                lock.release()
                time.sleep(0.1) #let someone else try to do something
                lock.acquire()
                lt = datetime.now()
                #if we wait too long, let our client just start a new request
                if int((lt - ct).total_seconds()) >= TIMEOUT:
                    response['status'] = 'failure'
                    response['reason'] = 'timeout'
                    break
            response['payload'] = data
            return json.dumps(response) #send over the data
        except Exception as E:
            #file an error report
            response['status'] = 'failure'
            response['reason'] = str(E)
            return json.dumps(response)
        finally: #whenever we leave, no matter what we must release the lock
            lock.release()

    @cherrypy.expose
    def write(self, id, color):
        response = {'status': 'failure'}
        try:
            lock.acquire() #start critical section - we're modifying colors
            id = int(id)
            if id < 0 or id >= SIZE: #ensure id is valid
                raise ValueError('id must be between 0 and {}'.format(SIZE))

            #update color data
            data['colors'][id] = urllib.parse.unquote(color)

            if output: #if we are logging, then log
                output.write('{}|{}\n'.format(id, color))
                output.flush();

            #increment our version, to let people know there is new data
            data['v'] += 1
            response['status'] = 'success'
            return json.dumps(response)
        except Exception as E:
            response['reason'] = str(E)
            return json.dumps(response)
        finally:
            lock.release() #whenever we leave we release the lock!

if __name__ == '__main__':
    try:
        #read stored data
        with open("storage.txt") as f:
            for l in f:
                id, color = l.strip().split('|')
                data['colors'][int(id)] = color
                data['v'] += 1
    except:
        pass

    #set up logging
    output = open("storage.txt", "a+")

    #set up cherrypy
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.join(os.path.abspath(os.getcwd()), 'static'),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './',
            'tools.staticdir.index': 'index.html'
        },
        '/assets': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './assets'
        }
    }
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 80
    cherrypy.server.shutdown_timeout = 1
    cherrypy.quickstart(Page(), '/', conf)
