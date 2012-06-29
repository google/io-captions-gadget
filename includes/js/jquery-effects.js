
$(document).ready(function($) {
	
//	$('#captions').serialScroll({
//		items:'li',
//		prev:'a.scrollUp',
//		next:'a.scrollDown',
//		axis:'y',
//		duration:1200
//	});
	$('a.scrollUp').live('click', function() {
		Stream.scrolled = true;
		Stream.container.scrollTop(Stream.container.scrollTop() - 20);
	});
	$('a.scrollDown').live('click', function() {
		Stream.container.scrollTop(Stream.container.scrollTop() + 20);
		if(Stream.container.scrollTop() + Stream.container.height() < Stream.container.get(0).scrollHeight) {
			Stream.scrolled = false;
		}
	});
	
	GOOGLEIO.GENERIC.languageSelect();
	GOOGLEIO.GENERIC.setTextSize();
	GOOGLEIO.GENERIC.toggleCaptions();
	Stream.container = $('#captions');
	Stream.fetch();
	
});

$(window).resize(function() {

});

// *******************************************************************************************

GOOGLEIO = {
};

// *******************************************************************************************

GOOGLEIO.GENERIC = {
	
	languageSelect: function() {
		
		$('a.changeLanguge').live('click', function() {
			if($('ul.languageList').is(":visible")) {
				$('ul.languageList').slideUp('fast');
				$('a.changeLanguge').removeClass('open');
			}
			else {
				$('ul.languageList').slideDown('fast');
				$('a.changeLanguge').addClass('open');
			}
			return false;
		});
		$('body').live('click', function() {
			$('ul.languageList').slideUp('fast');
			$('a.changeLanguge').removeClass('open');
			return false;
		});
		
		$('a.languageChoice').live('click', function() {
			var lang = $(this).attr('id').replace('lang-', '');
			$('li.active').removeClass('active');
			$(this).closest('li').addClass('active');
			Stream.setLang(lang);
			$('ul.languageList').fadeOut('fast');
			_gaq.push(['_trackEvent', 'Language', lang]);
			return false;
		});
		
	},
	
	setTextSize: function(){
		$('a.smallFontSize').live('click', function() {
			$('a.fontSizeLink').removeClass('active');
			$(this).addClass('active');
			$('body').removeClass('mediumText');
			$('body').removeClass('largeText');
			$('body').addClass('standardText');
			_gaq.push(['_trackEvent', 'TextSize', 'small']);
		});
		$('a.mediumFontSize').live('click', function() {
			$('a.fontSizeLink').removeClass('active');
			$(this).addClass('active');
			$('body').removeClass('standardText');
			$('body').removeClass('largeText');
			$('body').addClass('mediumText');
			_gaq.push(['_trackEvent', 'TextSize', 'medium']);
		});
		$('a.largeFontSize').live('click', function() {
			$('a.fontSizeLink').removeClass('active');
			$(this).addClass('active');
			$('body').removeClass('mediumText');
			$('body').removeClass('smallText');
			$('body').addClass('largeText');
			_gaq.push(['_trackEvent', 'TextSize', 'large']);
		});
	},
	
	toggleCaptions: function() {
		var openHeight = '100%';
		var closedHeight = $('.gadgetHeader').height();
		$('.captionButton').live('click', function() {
			$this = $(this);
			if($this.hasClass('on')) {
				//turn off:
				$this.removeClass('on').addClass('off');
				Stream.run = false;
				if(Stream.currentFetch) {
					Stream.currentFetch.abort();
				}
				Stream.container.html('');
//				$('.gadgetContent').hide();
				$('.gadgetWrapper').animate({height:closedHeight}, 'slow')
				$this.attr('title', 'Captions off, click to turn on.');
				_gaq.push(['_trackEvent', 'Captions', 'off']);
			}
			else {
				//turn off:
				Stream.run = true;
				Stream.container.html('');
				Stream.fetch();
				$this.removeClass('off').addClass('on');
//				$('.gadgetContent').show();
				$('.gadgetWrapper').animate({height:openHeight}, 'slow')
				$this.attr('title', 'Captions on, click to turn off.');
				_gaq.push(['_trackEvent', 'Captions', 'on']);
			}
		});
	}
};

// *******************************************************************************************
Stream = {
	run: true,
	fetchDelay: 750,
	baseDelay: 750,
	maxDelay: 1000 * 30,
	maxRetries: 10,
	emptyLimit: 1000,
	emptyFetches: 0,
	errors: 0,
	currentFetch: null,
	scrolled: false,
	running: false,
	displayDelay: 0,
	fetch: function() {
		if(!Stream.run || Stream.running) { return;}
		Stream.running = true;
		var last = Stream.lasts[Stream.eventId];
		var url = "/update?last=" + last + '&lang=' + Stream.lang + '&event=' + Stream.eventId;
		Stream.currentFetch = $.getJSON(url, function(response, status) {
			if(response) {
				// if there's a downward change in the delay, then ramp-down gradually instead of all at once,
				// which can result in garbled text, as later fragements get shown before earlier ones
				var delay = Math.max(response.delay_ms || 0, Stream.displayDelay - Stream.fetchDelay);
				Stream.displayDelay = delay;
				setTimeout(function() {
					Stream.container.html(Stream.runDeletes(Stream.container.html() + response.output));
				}, delay);
				if(!Stream.scrolled) {
					Stream.fixScroll();
				}
	   			if(response.status == 'stopped') {
	   				Stream.messageAdd("No event currently in progress.")
	   				$('#eventTitle').html('No event in progress');
	   				$('#liveNow').hide();
	   			}
	   			else {
	   				$('#eventTitle').html(response.title);
	   				$('#liveNow').show();
	   			}
	   			if(response.last == last) {
	   				Stream.emptyFetches++;
	   				if(Stream.emptyFetches > 1) {
	   					Stream.fetchDelay = Stream.fetchDelay * 2;
	   					Stream.fetchDelay = Math.min(Stream.maxDelay, Stream.fetchDelay * 2);
	   				}
	   			}
	   			else {
	   				Stream.emptyFetches = 0;
	   			}
	   			if(Stream.emptyFetches > Stream.emptyLimit) {
	   				Stream.messageAdd("There hasn't been any new content for a while...");
	   			}
	   			else {
	   				if(response.output != '') {
	   					Stream.messageClear();
	   				}
	   				Stream.lasts[Stream.eventId] = response.last;
	   			}
			}
			Stream.running = false;
			setTimeout(function() {
				Stream.fetch();
			}, Stream.fetchDelay);
   		}).error(function() {
   			Stream.errors++;
   			Stream.fetchDelay = Math.min(Stream.maxDelay, Stream.fetchDelay * 2);
   			Stream.running = false;
   			if(Stream.errors <= Stream.maxRetries) {
   				setTimeout(function() {
   					Stream.fetch();
   				}, Stream.fetchDelay);
   			}
   			else {
   				Stream.messageAdd("There seems to be a problem, try reloading");
   			}
   		})
   		.success(function() {
   			errors = 0;
   			Stream.fetchDelay = Stream.baseDelay;
   		});
	},
	
	fixScroll: function() {
		Stream.container.animate({scrollTop:Stream.container.get(0).scrollHeight}, 'slow');
//		var current = Stream.container.scrollTop() + Stream.container.height();
//		var full = Stream.container.get(0).scrollHeight;
//		if(current < full) {
//			Stream.container.animate({scrollTop: Stream.container.scrollTop()+20}, 'slow')
//			setTimeout(Stream.fixScroll, 500);
//		}
	},
		
	setLang: function(l) {
		if(l != Stream.lang) {
			Stream.lang = l;
			Stream.scrolled = false;
			Stream.messageAdd("Machine translation loading&hellip;", "<span class='poweredBy'>Powered by Google Translate</span>");
			Stream.currentFetch.abort();
			if($.inArray(l, Stream.rtl_langs) != -1) {
				Stream.container.css('direction', 'rtl');
			}
			else {
				Stream.container.css('direction', 'ltr');
			}
		}
	},
	
	setEvent: function(e) {
		if(e != Stream.eventId) {
			Stream.eventId = e;
			Stream.container.html('');
			Stream.currentFetch.abort();
		}
	},
	
	runDeletes: function(text) {
		var parts = (text + ' ').split('\b');
		var out = '';
		for(var i = 0; i < parts.length; i++) {
			out += parts[i];
			out = out.substr(0, out.length - 1);
		}
		return out;
	},
	
	messageAdd: function(text, sub) {
		sub = sub || ''
		Stream.container.html('');
		$('#messageBox').html('<h2>' + text + '</h2>' + sub).fadeIn('fast');
	},
	
	messageClear: function() {
		$('#messageBox').fadeOut('fast');
	}
}
// *******************************************************************************************

// *******************************************************************************************

// *******************************************************************************************