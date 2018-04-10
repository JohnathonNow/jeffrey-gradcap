#!/usr/bin/env python3
import cherrypy
from cherrypy.lib import static
import os
import urllib
import json
import threading
import time
from datetime import datetime

TIMEOUT = 30

colors={'cell_{}'.format(x): 'rgb(0,0,0)' for x in range(0, 32*32)}
colors['v'] = 1

output = None
lock = threading.Lock()

class Page(object):
    @cherrypy.expose
    def read(self, v):
        ct = datetime.now()
        try:
            lock.acquire()
            while int(v) >= int(colors['v']):
                lock.release()
                time.sleep(0.1)
                lock.acquire()
                lt = datetime.now()
                if int((lt - ct).total_seconds()) >= TIMEOUT:
                    break
            return json.dumps(colors)
        except Exception as E:
            return json.dumps({'Error': str(E)})
        finally:
            lock.release()

    @cherrypy.expose
    def write(self, id, color):
        try:
            lock.acquire()
            colors[id] = urllib.parse.unquote(color)
            output.write('{}|{}\n'.format(id, color))
            output.flush();
            colors['v'] += 1
            return 'success'
        except Exception as E:
            return str(E)
        finally:
            lock.release()

if __name__ == '__main__':
    with open("storage.txt") as f:
        for l in f:
            id, color = l.strip().split('|')
            colors[id] = color
    output = open("storage.txt", "a+")
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
