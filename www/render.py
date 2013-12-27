class Loader:
    def __init__(self, root):
        self.root = root
        self.engines

    def load(self, name):
        """
        The cases:
        resource.endpoint.format
        resource.endpoint.format.renderer
        resource.endpoint.format.renderer.renderer

        {root}/{resource}/{endpoint}.{format}.{engine}
        """




def template(template, context):
    return template.format(context)

