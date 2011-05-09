from google.appengine.api import memcache
import logging, re
from google.appengine.ext import deferred
from time import sleep
from translation import googletranslate
from google.appengine.ext import db
import config
import streamtext as stream
from tokenizer import CompromiseTokenizer as SentenceTokenizer
import os
import google.appengine.runtime

"""
>> optionally followed by someone's name and a :
e.g. >>NICK: SOME TEXT
or
>>NICK SMITH: SOME TEXT
or
>> SOME TEXT
for an unknown speaker
"""
speaker_id_pattern =  re.compile('(>>(?:\s|\w[^:]+:\s))')                    

class Event(db.Model):
    cache_key = 'event-is-running-%s'
    name = db.StringProperty()
    streamtext_id = db.StringProperty()
    active = db.BooleanProperty()
    default_open = db.BooleanProperty(default=True)
    
    def stop(self):
        c_key = 'stream-can-run-%s' % self.streamtext_id
        memcache.delete(c_key)
        memcache.delete('current-sentence-en-%s' % self.streamtext_id)
        for lang, _name in config.languages:
            memcache.delete('stream-%s-%s' % (lang, self.streamtext_id))
    
        
active_events_cache_key = 'active-events'
def get_active_events():
    events = memcache.get(active_events_cache_key)
    if events is None:
        events = [e for e in Event.all().filter('active =', True)]
        memcache.set(active_events_cache_key, events, 2 * 60)
    return events


title_cache_key = 'event-title-%s'
def get_title(event_id):
    title = memcache.get(title_cache_key % event_id)
    if title is None:
        event = Event.all().filter('streamtext_id =', event_id).get()
        if event is not None:
            title =  event.name
            memcache.set(title_cache_key % event_id, title)
        else:
            title = ''
    return title

def get_stream(event = None, last = None, empty_count = 0):
    try:
        if 'Development' in os.environ.get('SERVER_SOFTWARE'):
            #we don't want the task to be blocking browser-polls
            i = 1
        else:
            i = 20
        c_key = 'stream-can-run-%s' % event
        delay = 0.5
        base_delay = 0.5
        max_empty = 5
        max_delay = 60
        if last is None:
            last = stream.get_current_position(event)
        while i > 0:
            can_run = memcache.get(c_key)
            if can_run is None or can_run != 'yes':
                logging.info("Stopped %s" % event)
                return
            memcache.set(c_key, 'yes')
            output = ''
            try:
                (output, new_last) = stream.get_fragments(event, last)
                delay = base_delay
                
                if output != '':
                    empty_count = 0
                    set_text_fragment(last, 'en', output, event)
                    sentence_add(output, last, event)
                else:
                    logging.info("No output")
                    empty_count += 1
                    if empty_count > max_empty:
                        logging.info("max_empty reached")
                        empty_count = 0
                        sentence_add(output, last, event, force_translate=True)
                logging.info("%s = %s" % (last, output))
                last = new_last
            except:
                delay = min(delay * 2, max_delay)
                if delay == max_delay and i > 10:
                    break
                logging.info("Fetch errored, backing off %d" % delay)
                
            i -= 1
            sleep(delay)
        #endwhile
        deferred.defer(get_stream, event, last, empty_count)
    except google.appengine.runtime.DeadlineExceededError:
        logging.info("Deadline exceeded, starting anew")
        deferred.defer(get_stream, event, last, empty_count)
    except Exception, e:
        logging.info(e)
        logging.error("Something unexpected happened, caught and will kick-off new try")
        deferred.defer(get_stream, event, last, empty_count)


def run_deletes(text):
    """
    Look for backspace characters in the string, and 'act' on them,
    removing the character that comes before
    """
    
    out = ''
    for chars in (text + ' ').split('\x08'):
        out += chars
        out = out[:-1]
    return out

def set_text_fragment(key, lang, text, event):
    key = int(key)
    cacheKey = 'stream-%s-%s' % (lang, event)
    fragment_life = 10 * 60
    fragments = memcache.get(cacheKey)
    if fragments is None:
        fragments = {}
    else:
        max_key = max(fragments.keys())
        if max_key > key: #test-event loops
            fragments = {}
    fragments = dict((k, v) for k, v in fragments.items() if int(k) > (key - 100))
    fragments[key] = text
    memcache.set(cacheKey, fragments) 

def get_text_fragments(lang, key, event):
    """
    Return a tuple containing the current max-key and the concatenated text since the passed-in key
    """
    cacheKey = 'stream-%s-%s' % (lang, event)
    fragments = memcache.get(cacheKey)
    if fragments is None:
        return (0,'')
    max_key = max(fragments.keys())
    concatenated_text = ''.join([v for k, v in sorted(fragments.items(), key = lambda x: x[0]) if int(k) > key])
    return (int(max_key), concatenated_text)

def sentence_add(new_text, lastKey, event, force_translate = False):
    """
    Check if the new_text contains 'end of sentence'.
    If not, then append it to the current 'buffer' and return.
    If it does, then append it to the buffer, and then kick off the translation.
    """
    
    cacheKey = 'current-sentence-en-%s' % event
    current = memcache.get(cacheKey)
    if current is None:
        current = ''
    
    tokenizer = SentenceTokenizer()
    possible_sentence = run_deletes(current + new_text)
    logging.info("Check for sentence: %s" % possible_sentence)
    contains_end_of_sentence = tokenizer.text_contains_sentbreak(possible_sentence)
    speaker_id_match = speaker_id_pattern.search(possible_sentence)
    
    if ((force_translate and current != '')
     or (speaker_id_match is not None and speaker_id_match.start() > 0) 
     or contains_end_of_sentence):
        
        if speaker_id_match is not None and speaker_id_match.start() > 0:
            logging.info("Buffer contains speaker-ID, we'll split it up to translate.")
            full_sentence = possible_sentence[:speaker_id_match.start()]
            next = possible_sentence[speaker_id_match.start():]
        elif contains_end_of_sentence:
            logging.info("Decided we should split this text now")
            sentences = tokenizer.sentences_from_text(possible_sentence)
            full_sentence = sentences[0]
            next = ' '.join(sentences[1:])
        elif force_translate:
            logging.info("Forcing translation of current buffer")
            full_sentence = possible_sentence
            next = ''
        memcache.set(cacheKey, next)
        logging.info("Sentence: %s" % full_sentence)
        deferred.defer(translate_for_all, full_sentence, lastKey, event, _queue='translations')
    else:
        next = run_deletes(current + new_text)
        memcache.set(cacheKey, next)

def translate_for_all(text, lastKey, event):
    """
    Loop over all of the languages and kick-off async url-fetches, 
    using the callback below
    """
    rpcs = {}
    (speaker_id, text) = separate_speaker_id(text)
    format_string = '%s'
    if speaker_id is not None:
        format_string = speaker_id + format_string
    if text.endswith("\n"):
        format_string = format_string + "\n"
        text = text[:-1]
    if text.startswith("\n"):
        format_string = "\n" + format_string
        text = text[1:]
    for lang, _name in config.languages:
        if should_translate(lang):
            rpc = googletranslate.get_rpc()
            rpc.callback = make_translate_callback(rpc, lang, lastKey, event, format_string)
            googletranslate.translate_async(rpc, text, lang)
            rpcs[lang] = rpc
    for lang, rpc in rpcs.items():
        rpc.wait()


def separate_speaker_id(text):
    '''
    If text contains a speaker ID (>>FRED: ) then we don't
    want to include that in the text we ask to be translated,
    but do want to re-attach it afterwards, so need to keep it
    '''
    match = speaker_id_pattern.match(text)
    speaker_id = None
    if match is not None:
        logging.info("Text contains speaker ID: %s" % match.group())
        speaker_id = match.group()
        text = text[match.end():]
    return (speaker_id, text)

def set_should_translate(lang):
    """
    Set a flag in memcache to indicate that someone is watching this language
    """
    memcache.set('should-translate-%s' % lang, True, 60)

def should_translate(lang):
    return memcache.get('should-translate-%s' % lang) is not None

def make_translate_callback(rpc, fromLang, lastKey, event, formatString = '%s'):
    """
    Get the rpc's result, and decode the Translate API response into translated-text,
    then save this against the key that we're passing in.
    
    Done like this as the callback doesn't get any arguments, and we need to have
    the arguments above in-scope.
    """
    
    def callback():
        (translated,_sourceLang) = googletranslate.decode_response(rpc.get_result(), fromLang)
        logging.info("Translated = %s" % translated)
        translated = formatString % translated
        set_text_fragment(lastKey, fromLang, translated + ' ', event)
    return callback

def format_for_output(output):
    """
    Turn new-lines into <br>,
    surround speaker-IDs with a span, classname=speaker.
    """
    output = output.replace("\n", '<br />')
    replace = r'<span class="speaker">\1</span>'
    output = speaker_id_pattern.sub(replace, output)
    # speaker-pattern has whitespace on inside, and that helps with translation
    # but want it moved for output
    output = output.replace(' </span>', '</span> ')
    return output
