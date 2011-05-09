'''
Same API as the streamtext fetcher, this is a bit easier to test with.
'populate' will read a timed-text XML file off disk and split it up into the datastore,
then the get_ methods iterate through it, 1 by 1 with a small delay, and will return
randomly different lengths of text.
'''
from google.appengine.ext import db
from google.appengine.api import memcache
import random
import logging
from time import sleep

class Fragment(db.Model):
    last = db.IntegerProperty()
    text = db.TextProperty()
    event = db.StringProperty()

class Stream(db.Model):
    position = db.IntegerProperty()

def get_max(event):
    cache_key = 'stream-test-max-%s' % event
    max_f = memcache.get(cache_key)
    if max_f is None:
        f = Fragment.all().order('-last').get()
        max_f = f.last
        memcache.set(cache_key, max_f, 2 * 60)
    return int(max_f)

def get_current_position(event):
    stream = Stream.get_by_key_name(event)
    if stream is None:
        position = 0
    else:
        position = stream.position
    if position >= get_max(event):
        stream = Stream.get_or_insert(event)
        stream.position = 0
        memcache.delete('stream-test-max-%s' % event)
        stream.put()
        position = 0
    return position

def get_fragments(event, last):
    sleep(0.2)
    num = random.randint(0,3)
    fragments = Fragment.all().filter('event =', event).filter('last >', last).order('last').fetch(num)
    output = ''
    new_last = last
    for fragment in fragments:
        output += fragment.text
        new_last = fragment.last
    if new_last != last:
        stream = Stream.get_or_insert(event)
        stream.position = new_last
        stream.put()
    return (output, new_last)

def populate(file, event):
    import xml.dom.minidom
    try:
        dom = xml.dom.minidom.parse(file)
    except:
        logging.error("Failed to parse file")
    fragments = dom.getElementsByTagName('span')
    existing = [f for f in Fragment.all(keys_only=True)]
    db.delete(existing)
    
    i = 0
    for f in fragments:
        f_models = []
        text = ''
        for node in f.childNodes:
            if node.nodeType == node.TEXT_NODE:
                text += node.data
        length = 10
        frag_strings = split_len(text, length)
        for f_string in frag_strings:
            i += 1
            frag = Fragment()
            frag.last = i
            frag.text = f_string
            frag.event = event
            f_models.append(frag)
        db.put(f_models)
        logging.info(i)
    logging.info("Done")
    
def split_len(seq, length):
    return [seq[i:i+length] for i in range(0, len(seq), length)]