from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from google.appengine.ext import deferred
from google.appengine.ext.webapp import template
import stream
import simplejson, logging
from translation import googletranslate
import config
from google.appengine.api import urlfetch
from google.appengine.api import memcache
import simplejson
from urllib import unquote
from time import sleep
from translation import googletranslate
from google.appengine.ext import db
import config
import streamtext

class MainHandler(webapp.RequestHandler):
    def get(self):
        pass

def main():
    application = webapp.WSGIApplication([('/_ah/warmup', MainHandler),
                                          ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
