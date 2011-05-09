from google.appengine.api import urlfetch
import simplejson
import urllib
import logging
import config
key = config.translate_key
	
apiUrl = 'https://www.googleapis.com/language/translate/v2?'
defaultParams = {
	'key': key
}

"""
Calls Google's Translate API and, with no 'to' or 'from' specified will
attempt to auto-detect the language and convert it to English (by magic!)
returns tuple of translatedText,detectedLanguage
"""
def translate(toTranslate, toLang = 'en', fromLang = None):
	
	params = defaultParams.copy()
	params.update({
		'q': toTranslate.encode('utf-8'),
		'target': toLang,
	})
	if fromLang is not None:
		params['source'] = fromLang
	result = urlfetch.fetch(apiUrl + urllib.urlencode(params))
	return decode_response(result, fromLang)

def decode_response(result, fromLang = None):
	try:
		json_result = simplejson.loads(result.content)
	except ValueError:
		return False
	try:
		translations = json_result['data']['translations']
	except KeyError:
		logging.info("no data->translations")
		logging.info(json_result)
		return '', ''
	if len(translations) == 0:
		logging.info("Length = 0")
		return '',''
	
	translatedText = translations[0]['translatedText']
	detectedLanguage = fromLang
	if 'detectedSourceLanguage' in translations[0]:
		detectedLanguage = translations[0]['detectedSourceLanguage']
	return translatedText, detectedLanguage

def get_rpc():
	return urlfetch.create_rpc()

def translate_async(rpc, toTranslate, toLang = 'en', fromLang = None):
	params = defaultParams.copy()
	params.update({
		'q': toTranslate.encode('utf-8'),
		'target': toLang,
	})
	if fromLang is not None:
		params['source'] = fromLang
	callUrl = apiUrl + urllib.urlencode(params)
	urlfetch.make_fetch_call(rpc, callUrl)
	return rpc
	
	