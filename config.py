# -*- coding: UTF-8 -*-

# List of enabled languages.
# Complete list of languages supported by the Google Translate API at:
# https://developers.google.com/translate/v2/using_rest#language-params
languages = [
    ('af', u'Afrikaans'),
    ('sq', u'Albanian'),
    ('ar', u'Arabic'),
    ('az', u'Azerbaijani'),
    ('eu', u'Basque'),
    ('be', u'Belarusian'),
    ('bg', u'Bulgarian'),
    ('ca', u'Catalan'),
    ('zh-CN', u'Chinese Simplified'),
    ('zh-TW', u'Chinese Traditional'),
    ('hr', u'Croatian'),
    ('cs', u'Czech'),
    ('da', u'Danish'),
    ('nl', u'Dutch'),
    ('eo', u'Esperanto'),
    ('et', u'Estonian'),
    ('tl', u'Filipino'),
    ('fi', u'Finnish'),
    ('fr', u'French'),
    ('gl', u'Galician'),
    ('ka', u'Georgian'),
    ('de', u'German'),
    ('el', u'Greek'),
    ('gu', u'Gujarati'),
    ('ht', u'Haitian Creole'),
    ('iw', u'Hebrew'),
    ('hi', u'Hindi'),
    ('hu', u'Hungarian'),
    ('is', u'Icelandic'),
    ('id', u'Indonesian'),
    ('ga', u'Irish'),
    ('it', u'Italian'),
    ('ja', u'Japanese'),
    ('ko', u'Korean'),
    ('la', u'Latin'),
    ('lv', u'Latvian'),
    ('lt', u'Lithuanian'),
    ('mk', u'Macedonian'),
    ('ms', u'Malay'),
    ('mt', u'Maltese'),
    ('no', u'Norwegian'),
    ('fa', u'Persian'),
    ('pl', u'Polish'),
    ('pt', u'Portuguese'),
    ('ro', u'Romanian'),
    ('ru', u'Russian'),
    ('sr', u'Serbian'),
    ('sk', u'Slovak'),
    ('sl', u'Slovenian'),
    ('es', u'Spanish'),
    ('sw', u'Swahili'),
    ('sv', u'Swedish'),
    ('ta', u'Tamil'),
    ('th', u'Thai'),
    ('tr', u'Turkish'),
    ('uk', u'Ukrainian'),
    ('ur', u'Urdu'),
    ('vi', u'Vietnamese'),
    ('cy', u'Welsh'),
    ('yi', u'Yiddish'),
]

# Indicate Right-To-Left languages
rtl_langs = [
    'ar',
    'iw',
    'fa',
    'yi',
]

# Important: Increment version for static includes whenever they are modified.
static_version = 20

# Google Translate API key to use for translation
# Get one from https://code.google.com/apis/console/#access (Billing required)
translate_key = ''

# Google Analytics ID to use for tracking
# Get one from http://www.google.com/analytics/
analytics_account = ''
