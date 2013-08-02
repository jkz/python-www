import os
import sys
import shutil

from www.core import exceptions
from www.server import responses
from www.rest import resources, endpoints

class Resource(resources.Resource):
    """
    A filesystem state.
    """
    root = None

    def fetch(self, uid):
        """
        Return the list of directory contents, or the contents of the file.
        """
        data = {'path': uid}

        if os.path.isdir(uid):
            data['type'] = 'directory'
            data['content'] = os.listdir(uid)
        elif os.path.isfile(uid):
            data['type'] = 'file'
            with open(uid) as handle:
                data['content'] = handle.read()
        else:
            raise exceptions.NotFound
        return data

    def replace(self, uid, representation):
        if os.path.isdir(uid):
            raise exceptions.Conflict("Target is a directory")
        with open(uid, 'w') as handle:
            handle.write(representation)

    def delete(self, uid):
        if os.path.isdir(uid):
            shutil.rmtree(uid)
        elif os.path.isfile(uid):
            os.remove(uid)
        else:
            raise exceptions.NotFound

class Endpoint(endpoints.One):
    def identify(self, request):
        print(self.resource.root + '/' + request['kwargs']['path'])
        return self.resource.root + '/' + request['kwargs']['path']

    def POST(self, request):
        data = self.resource.replace(request['identifier'])
        raise responses.Created(location=self.reverse(request, path=request['identifier']))
