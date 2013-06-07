import unittest

from www.social import twitter

class TestAuth(unittest.TestCase):
    def test_signature_twitter(self):

        consumer = twitter.Consumer(
            key = 'xvz1evFS4wEEPTGEFPHBog',
            secret = 'kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw',
        )

        consumer = twitter.Consumer(
            key = 'MwRrwWfkoOWZy04IVt61qQ',
            secret = '1je9e4cIMdd5xCulGCV4Cy4HDLMtuCWlBR4LcgPsPk',
        )

        token = twitter.Token(
            key = '370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb',
            secret = 'LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE',
        )

        data = consumer.authority.get_request_token()
