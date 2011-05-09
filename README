A gadget to display captions processed via Streamtext for display next to a video-feed, for example.
Written in Python, runs on Google App Engine.
Code available from http://code.google.com/p/io-captions-gadget/


You'll need:
 - an application on Google App Engine: http://google.com/appengine
 - for translation, you'll need a Translate API key: https://code.google.com/apis/console/
 - an account with Streamtext (the person doing the transcribing needs the account): http://streamtext.net/

To get started:
 - checkout the code and with the App Engine SDK, choose "Create new application" and point it at the root of the checkout.
 - load the URL it's running on (http://localhost:XXXX) in your browser, and you should see the yellow/blue app, with a message saying there's no event running.
 - to start an event, visit /admin, tick the box to say you're an administrator, then enter 'IHaveADream' into the Event ID field, 'Martin Luther King' (for example) into the Title field and hit Save
 - when that reloads, there'll be an event listed at the bottom with Status "Not Running". Click "Start" next to it.
 - running locally, with the single-threaded server, things are a bit jerky, but if you look back to the gadget, you should start to see the text appear.
 - hit "Deploy" in the App Engine SDK to get it running on your App Engine account (and repeat the admin setup).
 
 Configuration:
  - config.py contains a few values that you can easily change:
    - the list of language you want to offer to viewers. 
     (Translation is only done for languages that actually have people watching, but running a long event with lots of translation will likely use up the 'courtesy quota' the Translate API provides).
    - the list of languages that should be displayed right-to-left.
    - a space for you to enter your Translate API key
    - an (optional) space for you to enter a Google Analytics account ID (the code beginning UA-). It will track use of the gadget, firing events for language selection, text-size changes and for opening/closing (pausing) the captions.
  - the admin page (accessible to anyone who is an admin on the App Engine account) lets you configure two events to be running simultaneously. You could increase this to more if needed, but how that performs hasn't been tested.   