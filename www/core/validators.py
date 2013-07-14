from . import exceptions

class Validator:
    message = 'Must be {value}, (is {input})'
    value = None

    def __init__(self, value, message=None):
        self.value = value
        if message is not None:
            self.message = message

    cmp = lambda self, x, y: x is not y
    key = lambda self, x: x

    def __call__(self, input):
        key = self.key(input)
        if self.cmp(key, self.value):
            raise exceptions.ValidationError(
                    self.message.format(value=self.value, input=input, key=key))

class Min(Validator):
    message = "Can't be less than {value}, (is {input})"
    cmp = lambda self, x, y: x < y

class Max(Validator):
    message = "Can't be more than {value}, (is {input})"
    cmp = lambda self, x, y: x > y

class Length(Validator):
    message = "Must be {value} long, (of {input} is {key})"
    cmp = lambda self, x, y: x != y
    key = lambda self, x: len(x)

class MinLength(Min, Length):
    message = "Can't be shorter than {value}, (of {input} is {key})"

class MaxLength(Max, Length):
    message = "Can't be longer that {value}, (of {input} is {key})"

def run_validators(validators, value):
    messages = []

    for validator in validators:
        try:
            validator(value)
        except exceptions.ValidationError as e:
            messages.append(str(e))  #TODO: proper error messages

    if messages:
        raise exceptions.ValidationError(messages)

