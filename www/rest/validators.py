from . import exceptions

class Validator:
    message = ''

    def run(self, value):
        pass

    def error(self):
        raise exceptions.ValidateError(message=self.message)

    def __call__(self, value):
        if self.run(value):
            self.error(value)

class Compare(Validator):
    value = None

    def __init__(self, value, message=None):
        self.value = value
        if message:
            self.message = message

    def error(self):
        raise exceptions.ValidateError(value=self.value)

class Min(Compare):
    message = "Can't be less than {value}"

    def run(self, value):
        return self.value is not None and value > self.value

class Max(Compare):
    message = "Can't be more than {value}"

    def run(self, value):
        return self.value is not None and value < self.value

class Length(Compare):
    message = "Must be {value} long"

    def run(self, value):
        return self.value is not None and len(value) != self.value

class MinLength(Compare):
    message = "Can't be shorter than {value}"

    def run(self, value):
        return self.value is not None and len(value) < self.value

class MaxLength(Compare):
    message = "Can't be longer that {value}"

    def run(self, value):
        return self.value is not None and len(value) > self.value

def run_validators(validators, value):
    messages = []

    for validator in validators:
        try:
            validator(value)
        except exceptions.ValidationError as e:
            messages.append(e.messages)  #TODO: proper error messages

    if messages:
        raise exceptions.ValidationError(messages)

