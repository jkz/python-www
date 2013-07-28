from . import methods

# Namespace api
def implement_methods(function, namespace):
    """
    Adds `open` and lowercased versions of each method to the namespace,
    to invoke request objects created by given function.
    """
    namespace['open'] = lambda url, **kwargs: function(url=url, **kwargs)()

    for method in methods.ALL:
        namespace[method.lower()] = functools.partial(namespace['open'], method=method)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

