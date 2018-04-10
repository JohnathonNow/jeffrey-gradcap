#!/usr/bin/env python3
import cherrypy
from cherrypy.lib import static
import os
import urllib
import json
import threading
import time
from datetime import datetime

TIMEOUT = 30 #timeout for requests, for long polling

#initialize grid to all black
colors={'cell_{}'.format(x): 'rgb(0,0,0)' for x in range(0, 32*32)}
#keep track of a "version number" for detecting changes
colors['v'] = 1
#log changes to output file
output = None
#a lock for thread safety
lock = threading.Lock()

class Page(object):
    @cherrypy.expose
    def read(self, v):
        ct = datetime.now() #get the start time, for long polling
        try:
            lock.acquire()
            while int(v) >= int(colors['v']): #wait for new data
                lock.release()
                time.sleep(0.1) #let someone else try to do something
                lock.acquire()
                lt = datetime.now()
                #if we wait too long, let our client just start a new request
                if int((lt - ct).total_seconds()) >= TIMEOUT:
                    break
            return json.dumps(colors) #send over the data
        except Exception as E:
            #file an error report
            return json.dumps({'Error': str(E)})
        finally: #whenever we leave, no matter what we must release the lock
            lock.release()

    @cherrypy.expose
    def write(self, id, color):
        try:
            lock.acquire() #start critical section - we're modifying colors
            colors[id] = urllib.parse.unquote(color)
            if output: #if we are logging, then log
                output.write('{}|{}\n'.format(id, color))
                output.flush();
            #increment our version, to let people know there is new data
            colors['v'] += 1
            return 'success'
        except Exception as E:
            return str(E)
        finally:
            lock.release() #whenever we leave we release the lock!

if __name__ == '__main__':
    try:
        #read stored data
        with open("storage.txt") as f:
            for l in f:
                id, color = l.strip().split('|')
                colors[id] = color
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
