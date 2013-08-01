from www.core import http
from www.content import negotiate

class Request(http.Request):
    @property
    def path(self):
    	if 'path' in self:
    		return self['path']
        return self.url.absolute

    @property
    def content_type(self):
    	if 'content_type' in self:
    		return self['content_type']
    	elif 'Content-Type' in self.headers:
    		return negotiate.type(self.headers['Content-Type'])
		elif 'CONTENT_TYPE' in self:
			return negotiate.type(self['CONTENT_TYPE'])

    @property
    def content_length(self):
    	if 'content_length' in self:
    		return self['content_length']
    	elif 'Content-Length' in self.headers:
    		return int(self.headers['Content-Length'])
    	elif 'CONTENT_LENGTH' in self:
    		return int(self['CONTENT_LENGTH'])
        return len(self.body)

    @property
    def accept(self):
    	if 'accept' in self:
    		return self['accept_type']
    	elif 'Accept' in self.headers:
    		return negotiate.range(self.headers['Accept'])
    	elif 'HTTP_ACCEPT' in self:
    		return negotiate.range(self['HTTP_ACCEPT'])

    @property
    def language(self):
    	if 'language' in self:
    		return self['language']
    	elif 'Content-Language' in self.headers:
    		return self.headers['Content-Language']
    	elif 'CONTENT_LANGUAGE' in self:
    		return self['CONTENT_LANGUAGE']
