from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from google.appengine.ext import deferred
from google.appengine.ext import db
from google.appengine.ext.webapp import template
import stream
import logging

class AdminHandler(webapp.RequestHandler):
    
    def get(self):
        path = 'templates/admin.html'
        e1 = stream.Event.get_by_key_name('e1')
        e2 = stream.Event.get_by_key_name('e2')
        statuses = {}
        events_list = [e1, e2]
        for e in events_list:
            if e is None or e.streamtext_id is None or e.streamtext_id == '':
                continue
            statuses[e.streamtext_id] = memcache.get('stream-can-run-%s' % e.streamtext_id) is not None
        logging.info("STATUSES")
        logging.info(statuses)
        values = {
                  'events': events_list,
                  'statuses': statuses,
        }
        self.response.out.write(template.render(path, values))
    def post(self):
        
        events = []
        for i in [1, 2]:
            event_id = self.request.get('event%d' % i )
            logging.info(event_id)
            e = stream.Event.get_by_key_name('e%d' % i)
            if e is None:
                e = stream.Event(key_name='e%d' % i)
            elif e.streamtext_id != event_id:
                e.stop()
            e.streamtext_id = event_id
            if event_id != '':
                e.name = self.request.get('title%d' % i, 'Stream %d' % i)
                open =  self.request.get('open%d' % i) == 'on'
                e.default_open = open
                memcache.set(stream.title_cache_key % event_id, e.name)
                e.order = 1
                e.active = True
                try:
                    e.delay_ms = int(float(self.request.get('delay%d' % i, 0)) * 1000)
                except ValueError:
                    e.delay_ms = 0
            else:
                e.active = False
            events.append(e)
        
        db.put(events)
        memcache.delete(stream.active_events_cache_key)
        stream.get_active_events()
        self.redirect('/admin')
        

class ControlHandler(webapp.RequestHandler):
    
    def post(self):
        key = self.request.get('key')
        if key == '':
            self.response.out.write("No key")
            return
        control = self.request.get('control')
        event = stream.Event.all().filter('streamtext_id =', key).get()
        if event is None:
            self.response.out.write("No event")
            return
        c_key = 'stream-can-run-%s' % event.streamtext_id
        if control == 'Stop':
            event.stop()
        elif control == 'Start':
            if memcache.get(c_key) is None:
                deferred.defer(stream.get_stream, event.streamtext_id)
            memcache.set(c_key, 'yes')
        return self.redirect('/admin')
            

def main():
    application = webapp.WSGIApplication([('/admin', AdminHandler),
                                          ('/admin/control', ControlHandler),
                                          ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
