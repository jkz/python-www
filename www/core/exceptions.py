class Warning(Exception):
    pass

class Error(Warning):
    pass

class ValidationError(Error):
        pass

class Omitted(Warning):
    """A non-required key or attribute was not found"""
    pass

class Missing(Error):
    """A required key or attribute was not found"""
    pass


