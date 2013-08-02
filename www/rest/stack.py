from www.server import middleware
from www.server.stack import *

class Params(middleware.Option):
	params = 'method', 'accept', 'language'

	def method(self, request):
		if 'method' in request.url.query:
			return request.url.query['method']

	def accept(self, request):
		if 'kwargs' in request and 'format' in request['kwargs']:
			return request.kwargs['format']
		elif 'format' in request.url.query:
			return request.url.query['format']

	def language(self, request):
		if 'lang' in request.url.query:
			return request.url.query['lang']

	def resolve(self, request):
		for key in self.params:
			val = getattr(self, key)(request)
			if val is None:
				request[key] = val

class Defaults(middleware.Option):
	params = 'allowed_types', 'supported_types'

	allowed_types = 'json', 'form', 'text'
	supported_types = 'json',

	def resolve(self, request):
		for key in self.params:
			request[key] = getattr(self, key)

def build(router, *args, dispatcher=Dispatcher()):
	base = middleware.Stack([
		Excepts,
		Router(router),
		Defaults,
		Params,
		Content,
	])
	extra = middleware.Stack(args)
	return (base + extra)(dispatcher)