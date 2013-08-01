from www.server import middleware

class Params(middleware.Option):
	def accept(self, request):
		if 'kwargs' in request and 'format' in request['kwargs']:
			return request.kwargs['format']
		elif 'format' in request.url.query:
			return request.url.query['format']

	def language(self, request):
		if 'lang' in request.url.query:
			return request.url.query['lang']

	def resolve(self, request):
		for key in ['accept', 'language']:
			val = getattr(self, key)(request)
			if val is None:
				request[key] = val
