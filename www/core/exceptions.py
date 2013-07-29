class Raisable(BaseException):
    pass

class Info(Raisable):
    pass

class Success(Raisable):
    pass

class Warning(Exception, Raisable):
    """An advisory notification."""
    pass

# Error and Fault definitions from (I thought they were nice)
# http://vikashazrati.wordpress.com/2008/10/30/fault-failure-error/
class Error(Warning):
    """
    A discrepancy between a computed, observed, or measured value or condition
    and the true, specified, or theoretically correct value or condition.
    """
    pass

class Fault(Error):
    """
    An incorrect step, process, or data definition in a computer program which
    causes the program to perform in an unintended or unanticipated manner.
    """
    pass


class Invalid(Error):
    """A value did not pass a validation."""
    pass

class Omitted(Info):
    """A non-required key or attribute was not found."""
    pass

class Missing(Error):
    """A required key or attribute was not found."""
    pass


class MethodNotAllowed(Error):
    code = 405


