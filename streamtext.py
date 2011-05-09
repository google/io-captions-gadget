'''
Created on Apr 12, 2011

@author: admin
'''
import logging
from google.appengine.api import urlfetch
import simplejson
from urllib import unquote

streamUrl = 'http://www.streamtext.net/text-data.ashx?event=%s&last=%s'

def get_current_position(event):
    last = 0
    url = streamUrl % (event, str(last))
    # we only want to be join in at the point in the stream that's now,
    # no point getting everything right back from the beginning:
    response = urlfetch.fetch(url, method='HEAD')
    if 'l_p' in response.headers:
        last = response.headers['l_p']

def get_fragments(event, last):
    url = streamUrl % (event, str(last))
    response = urlfetch.fetch(url)
    if response.status_code != 200:
        logging.info("Event not running")
        raise StreamtextException("No event running")
    try:
        content = simplejson.loads(response.content)
    except ValueError, e:
        raise(e)
    output = ''
    for fragment in content['i']:
        output += unquote(fragment['d'])
    new_last = response.headers['l_p']
    return (output, new_last)

class StreamtextException(Exception):
    pass