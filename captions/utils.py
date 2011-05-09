def http_p3p(func):
    """
    Add the P3P headers to the response that makes Cookies work in an iframe
    in IE.
    """
    def set_header(self, **kwargs):
        self.response.headers['P3P'] = 'CP="CAO DSP COR CURa ADMa DEVa OUR IND PHY ONL UNI COM NAV INT DEM PRE"'
        func(self,**kwargs)
    return set_header
    
def http_cache_control(max_age = 0):
    '''decorator for requesthandler methods to set Cache-Control header
    
    will set Cache-Control: public, max-age=XX header on response
    Args:
      max_age: int specifying max-age in seconds
    '''
    def wrap(func):
        def set_header(self, **kwargs):
            self.response.headers["Cache-Control"] = 'public,max-age=%d' % max_age
            func(self, **kwargs)
        return set_header
    return wrap    