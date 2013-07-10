class Warning(Exception):
    pass

class Error(Warning):
    pass

class ValidationError(Error):
    pass

class Omitted(Warning):
    pass

class Missing(Error):
    pass


