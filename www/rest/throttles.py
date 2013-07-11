import math
import datetime

from . import exceptions
from . import guards

class Throttle(guards.Guard):
    """
    Throttler is the Keeper of the Bandwith.
    He manages rate limits of users. And replenishes shares of those
    in fixed intervals.
    """
    # in seconds
    interval = 60 * 60

    # decrement per call
    cost = 1

    # maximum points
    max = 300

    # number of points replenished per interval
    gain = 300

    def init(self, **kwargs):
        self.prefix = kwargs.get('prefix', '_throttle_')

    def key(self, request):
        return None

    def get(self, key):
        return None

    def set(self, key, pair, expire):
        pass

    def message(self, request, pair):
        return 'Rate limit reached, please slow down!'

    def now(self):
        return datetime.datetime.now()


    def _update_pair(self, pair):
        now = self.now()
        if pair:
            value, stamp = pair
            ticks = (now - stamp).total_seconds() // self.interval
            value = min(value + ticks * self.gain, self.max)
            seconds = datetime.timedelta(seconds=ticks * self.interval)
            stamp = min(stamp + seconds, now)
        else:
            value = self.max
            stamp = now
        return value, stamp

    def _timeout(self, value):
        return math.ceil((self.max - value) / self.gain) * self.interval

    def call(self, request):
        # Get the key from the request
        key = self.prefix + self.key(request)

        # Get the value and timestamp from storage backend
        pair = self.get(key)

        # Update pair for new timestamp
        value, stamp = self._update_pair(pair)

        # Set the return value
        allowed = value > self.cost

        # Subtract the value from the pool if allowed
        if allowed:
            value -= self.cost

        # Calculate the expiry time
        timeout = self._timeout(value)

        pair = value, stamp

        # Store the new value, timestamp pair in the backend
        self.set(key, pair, timeout)

        if not allowed:
            message = self.message(pair, request)
            raise exceptions.TooManyRequests(message)

