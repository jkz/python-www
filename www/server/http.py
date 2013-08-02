from www.content import negotiate
from www.core.http import *

class Method(Method):
    def __get__(self, obj, cls):
        if obj and 'method' in obj:
            return obj['method']
        return super().__get__(obj, cls)

class Request(Request):
    method = Method()

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
            return negotiate.type(self['allowed_types'], self.headers['Content-Type'])

    @property
    def content_length(self):
        if 'content_length' in self:
            return self['content_length']
        elif 'Content-Length' in self.headers:
            return int(self.headers['Content-Length'])

    @property
    def content(self):
        return self.body.read(self.content_length).decode('utf-8')

    @property
    def accept(self):
        if 'accept' in self:
            return self['accept']
        elif 'Accept' in self.headers:
            return negotiate.range(self['supported_types'], self.headers['Accept'])

    @property
    def language(self):
        if 'language' in self:
            return self['language']
        elif 'Content-Language' in self.headers:
            return self.headers['Content-Language']

