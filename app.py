#!/usr/bin/env python3
import cherrypy
from cherrypy.lib import static
import os

class Page(object):
    @cherrypy.expose
    def index(self):
        return "<html><h1>Welcome to my project</h1></html>"
if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
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
