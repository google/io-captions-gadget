from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from google.appengine.ext import deferred
from google.appengine.ext.webapp import template
import test_stream.stream
import simplejson, logging
import config

class MainHandler(webapp.RequestHandler):
    def get(self):
        event = self.request.get('event', 'test')
        deferred.defer(test_stream.stream.populate, 'timedtext.xml', event)

def main():
    application = webapp.WSGIApplication([('/testfill', MainHandler),
                                          ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
