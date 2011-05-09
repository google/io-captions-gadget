"""
Different methods of splitting text before we send it to be translated.
NL analysis doesn't work too well, because it relies on words following a break, which
we'll often not get (if there are pauses).
Breaking on .?! can result in too-long gaps between text appearing for the translated languages.
"""

import re
#capture-group means that .split will contain the separators
sentence_ending_punctuation = re.compile(r'([.!?])')
class PunctuationBasedTokenizer():
    """
    Split for translation whenever the text contains a full-stop, question-mark or exclamation-mark.
    Will 'break' with acronyms, abbreviations or initials, and from testing can result in quite long
    delays when given typed speech.
    """
    
    def text_contains_sentbreak(self, text):
        """
        Return true iff text looks like it contains a sentence-break
        """
        match = sentence_ending_punctuation.search(text)
        return match is not None
    
    def sentences_from_text(self, text):
        """
        Take a string of text, and return a list of strings that look like sentences
        """
        split_text = sentence_ending_punctuation.split(text)
        #except the punctuation isn't attached, and it might be useful
        sentences = []
        for sent in split_text:
            if len(sentences) > 0 and sentence_ending_punctuation.match(sent):
                sentences[-1] += sent
            else:
                sentences.append(sent)
        return sentences
    
class CompromiseTokenizer():
    """
    Compromise between getting some context for translation vs. keeping text
    in sync with video. Breaks text on newlines and every X characters
    (35 is common line-length for captions.)
    """
    char_limit = 35
    
    def text_contains_sentbreak(self, text):
        limit_match = len(text) > self.char_limit
        newline_match = "\n" in text and text.index("\n") > 5
        return limit_match or newline_match
    
    def sentences_from_text(self, text):
        if "\n" in text:
            index = text.index("\n")
            #keep the newline on the end of the first half
            before = text[:index+1]
            after = text[index+1:]
            sentences = [before, after]
        else:
            point = self.char_limit
            while point >= 0 and text[point] != ' ':
                point -= 1
            if point == 0:
                #if we have a word > 35chars, not much else we can do
                point = self.char_limit
            sentences = [text[:point], text[point:]]
        return sentences
            