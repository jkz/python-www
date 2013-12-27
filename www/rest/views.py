from www.server import middleware
from . import stack

class Engine(middleware.Layer):
    def render(self, template, context={}, data={}):
        return 'This should be a render of {} for {} in {}'.format(
            template, data, context)

    def resolve(self, request):
        data = self.application(request)
        return self.render(request['template'], request, data)

class Render(stack.Render):
    def render(self, request, data):
        # Select an engine based on file extension
        engine = 'TODO'
        template = request['template']
        context = request.copy()
        context['data'] = data
        engine.render(template, context)

        engine.render(template, data, request, data)

class Template(middleware.Render):
    def render(self, request, data):
        template = request['template']


class Finder(middelware.Option):
    def resolve(self, request):
        request['template'] = None

class View:
    """
    Prepares a context which it passes to a template.

    Special diretory '/views' is the default location for templates.
    Subdirectories with resource names hold the actual template files.
    Special subdirectory '/defaults' is searched when the resource directory
    or the template inside is missing.
    The templates are found by resource name.
    """
    template = None

    def __init__(self, template):
        if template:
            self.template = template
