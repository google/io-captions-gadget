from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
import stream
import simplejson, logging
import config
from captions import utils

class MainHandler(webapp.RequestHandler):
    @utils.http_cache_control(30)
    @utils.http_p3p
    def get(self):
        lang = self.request.get('lang', 'en')
        is_android = self.request.get('android', 'f')
        force_open = self.request.get('open', 'false')
        theme = self.request.get('theme', 'light')
        is_auto_open = self.request.get('open_sesame', 'false') != 'false'
        lasts = {}
        if is_android == 't':
            path = 'templates/captions-android.html'
        else:
            path = 'templates/captions.html'
        events = stream.get_active_events()
        if len(events) == 0:
            start_event = None
            last = None
        else:
            for event in events:
                (last, _out) = stream.get_text_fragments(lang, 0, event.streamtext_id)
                lasts[event.key().name()] = last
            
            start_event_id = self.request.get('event')
        
            start_event = events[0]
            if start_event_id != '':
                for e in events:
                    if e.key().name() == start_event_id:
                        start_event = e
        values = {
            'auto_open': is_auto_open,
            'last' : last,
            'lang': lang,
            'languages': config.languages,
            'events': events,
            'event': start_event,
            'lasts': simplejson.dumps(lasts),
            'ga_account': config.analytics_account,
            'rtl_langs': simplejson.dumps(config.rtl_langs),
            'static_version': config.static_version,
            'force_open': force_open != 'false',
            'theme': theme,
        }
        self.response.out.write(template.render(path, values))

class Update(webapp.RequestHandler):
    '''
    Endpoint for Ajax requests. Returns most recent fragments of test for the specified event in the specified language
    , along with title and status for the event. Output is memcached for 1 second, keyed by lang/event/last-id
    '''
    def get(self):
        lang = self.request.get('lang', 'en')
        last = int(self.request.get('last'))
        event_name = self.request.get('event')
        events = stream.get_active_events()
        event_key = None
        event = None
        for e in events:
            if e.key().name() == event_name:
                event = e
                event_key = e.streamtext_id
        if event_key is None:
            return
        cacheKey = 'output-%s-%s-%s' % (lang, last, event_key)
        outputCacheTime = 1
        max_age = 1
        response = memcache.get(cacheKey)
        if response is None:
            stream.set_should_translate(lang)
            (new_last, output) = stream.get_text_fragments(lang, last, event_key)
            if memcache.get('stream-can-run-%s' % event_key) == 'yes':
                status = 'running'
            else:
                status = 'stopped'
            output = stream.format_for_output(output)
            response = simplejson.dumps({
                'last': new_last,
                'output': output,
                'status': status,
                'title': stream.get_title(event_key),
                'delay_ms': event.delay_ms
            })
            if output != '':
                outputCacheTime = 5
                max_age = 5
            memcache.set(cacheKey, response, outputCacheTime)
        else:
            decoded = simplejson.loads(response)
            if decoded['output'] != '':
                max_age = 5
        self.response.headers['Cache-Control'] = 'public,max-age=%s' % max_age
        self.response.out.write(response)
        
        
def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/update', Update),
                                          ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
