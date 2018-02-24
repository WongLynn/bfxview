import requests
import json
import base64
import hashlib
import hmac
try:
    from urllib.parse import quote, urlencode
except:
    from urllib import quote, urlencode
import time #for nonce

class GateIOClient(object):
    BASE_URL = "http://data.gate.io/api2/1"

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.name = 'gateio'
        app.extensions[self.name] = self
        self.api_key = app.config[self.name.upper()+'_API_KEY']
        self.api_secret = app.config[self.name.upper()+'_API_SECRET']

    def _timestamp(self):
        return str(int(round(time.time() * 1000)))

    def _post_data_auth(self, path, params):
        string = urlencode(params)
        h = hmac.new(self.api_secret, string, hashlib.sha512)
        signature = h.hexdigest()
        headers = {
            'KEY': self.api_key,
            'SIGN': signature
        }

        r = requests.post(
            self.BASE_URL + path,
            data=params,
            headers=headers
        )
        if r.status_code == 200:
            return r.json()

    @property
    def wallets(self):
        params = {}
        data = self._post_data_auth('/private/balances', params)
        return data

    def get_balances(self):
        params = {}
        data = self._post_data_auth('/private/balances', params)['available']
        return [
            {
                'exchange': self.name,
                'asset': a,
                'balance': float(b)
            }
            for a, b in data.items()
        ]
