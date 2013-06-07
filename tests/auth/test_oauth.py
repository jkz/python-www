import unittest

import www
from www.auth import oauth

class TestAuth(unittest.TestCase):
    def test_signature_tumblr(self):
        consumer = oauth.Consumer(
            key = 'xnr8wCo3LynwHN5G4EpPgvEnLsQsFh17QuT2rNpUrnl0JdwjZO',
            secret = 'u6FxwVOPmoW5yrXV7ZmXd8IxYYOVaSQ9w4Q5UAHaKApOHLEhn2')

        token = oauth.Token(
            key = 'lTdTm5rKIhRKwlqtjoFgiDxuEgDefr1BYaLNXqfGwpn6Ro2FCC',
            secret = 'dgZBLLF0MaVeHAfXOT79lVWZvqQ4oSXhMFvCFV3EUtIDb4PomJ')

        auth = oauth.Auth(consumer, token)

        method = 'POST'
        base_url = 'http://www.tumblr.com/oauth/access_token'
        params_dict = dict(
            oauth_verifier = 'aOPAHwBJBUqjPUP3LT9JzJ08ywleE2xLTk1FgOwrh9rEUlj80f',
        )
        header_dict = dict(
            oauth_consumer_key = auth.consumer.key,
            oauth_nonce = '17616581727913238353',
            oauth_signature_method = 'HMAC-SHA1',
            oauth_timestamp = '1353470277',
            oauth_token = auth.token.key,
            oauth_version = '1.0',
        )

        combo_dict = {}
        combo_dict.update(params_dict)
        combo_dict.update(header_dict)
        sorted_dict = sorted(combo_dict.items())
        params_string = www.urlencode(sorted_dict)
        computed_param_string = params_string.replace('+', '%20').replace('%7E', '~')

        expected_param_string = "oauth_consumer_key=xnr8wCo3LynwHN5G4EpPgvEnLsQsFh17QuT2rNpUrnl0JdwjZO&oauth_nonce=17616581727913238353&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1353470277&oauth_token=lTdTm5rKIhRKwlqtjoFgiDxuEgDefr1BYaLNXqfGwpn6Ro2FCC&oauth_verifier=aOPAHwBJBUqjPUP3LT9JzJ08ywleE2xLTk1FgOwrh9rEUlj80f&oauth_version=1.0"
        self.assertEqual(expected_param_string, computed_param_string)

        expected_base_string = "POST&http%3A%2F%2Fwww.tumblr.com%2Foauth%2Faccess_token&oauth_consumer_key%3Dxnr8wCo3LynwHN5G4EpPgvEnLsQsFh17QuT2rNpUrnl0JdwjZO%26oauth_nonce%3D17616581727913238353%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1353470277%26oauth_token%3DlTdTm5rKIhRKwlqtjoFgiDxuEgDefr1BYaLNXqfGwpn6Ro2FCC%26oauth_verifier%3DaOPAHwBJBUqjPUP3LT9JzJ08ywleE2xLTk1FgOwrh9rEUlj80f%26oauth_version%3D1.0"
        computed_base_string = oauth.build_base_string(method, base_url, computed_param_string)
        self.assertEqual(expected_base_string, computed_base_string)

        expected_signature = 'APWCxCfDVNwB1gI/Gntz3Ftmp7c='
        computed_signature = auth.signature(computed_base_string)
        self.assertEqual(expected_signature, computed_signature)

    def test_signature_twitter(self):
        consumer = oauth.Consumer(
            key = 'xvz1evFS4wEEPTGEFPHBog',
            secret = 'kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw')

        token = oauth.Token(
            key = '370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb',
            secret = 'LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE')

        auth = oauth.Auth(consumer, token)

        method = 'POST'
        base_url = 'https://api.twitter.com/1/statuses/update.json'
        params_dict = dict(
            status = 'Hello Ladies + Gentlemen, a signed OAuth request!',
            include_entities = 'true',
        )
        header_dict = dict(
            oauth_consumer_key = auth.consumer.key,
            oauth_nonce = 'kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg',
            oauth_signature_method = 'HMAC-SHA1',
            oauth_timestamp = '1318622958',
            oauth_token = auth.token.key,
            oauth_version = '1.0',
        )

        combo_dict = {}
        combo_dict.update(params_dict)
        combo_dict.update(header_dict)
        sorted_dict = sorted(combo_dict.items())
        computed_param_string = www.urlencode(sorted_dict)
        computed_param_string = computed_param_string.replace('+', '%20')

        expected_param_string = "include_entities=true&oauth_consumer_key=xvz1evFS4wEEPTGEFPHBog&oauth_nonce=kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1318622958&oauth_token=370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb&oauth_version=1.0&status=Hello%20Ladies%20%2B%20Gentlemen%2C%20a%20signed%20OAuth%20request%21"
        self.assertEqual(expected_param_string, computed_param_string)

        expected_base_string = "POST&https%3A%2F%2Fapi.twitter.com%2F1%2Fstatuses%2Fupdate.json&include_entities%3Dtrue%26oauth_consumer_key%3Dxvz1evFS4wEEPTGEFPHBog%26oauth_nonce%3DkYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1318622958%26oauth_token%3D370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb%26oauth_version%3D1.0%26status%3DHello%2520Ladies%2520%252B%2520Gentlemen%252C%2520a%2520signed%2520OAuth%2520request%2521"
        computed_base_string = oauth.build_base_string(method, base_url, computed_param_string)
        self.assertEqual(expected_base_string, computed_base_string)

        expected_signing_key = "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw&LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE"
        computed_signing_key = auth.signing_key
        self.assertEqual(expected_signing_key, computed_signing_key)


        expected_signature = 'tnnArxj06cWHq44gCs1OSKk/jLY='
        computed_signature = auth.signature(computed_base_string)
        self.assertEqual(expected_signature, computed_signature)

