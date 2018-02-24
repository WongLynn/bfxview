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

class GeminiClient(object):
    BASE_URL = "https://api.gemini.com"

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.name = 'gemini'
        app.extensions[self.name] = self
        self.api_key = app.config[self.name.upper()+'_API_KEY']
        self.api_secret = app.config[self.name.upper()+'_API_SECRET']

    def _timestamp(self):
        return str(int(round(time.time() * 1000)))

    def _post_data_auth(self, path, params):
        params['request'] = path
        params['nonce'] = self._timestamp()
        payload = base64.b64encode(json.dumps(params))
        h = hmac.new(self.api_secret, payload, hashlib.sha384)
        signature = h.hexdigest()
        headers = {
            'Cache-Control': 'no-cache',
            'Content-Length': '0',
            'Content-Type': 'text/plain',
            'X-GEMINI-APIKEY': self.api_key,
            'X-GEMINI-PAYLOAD': payload,
            'X-GEMINI-SIGNATURE': signature
        }

        r = requests.post(
            self.BASE_URL + path,
            headers=headers
        )
        if r.status_code == 200:
            return r.json()

    @property
    def wallets(self):
        params = {}
        data = self._post_data_auth('/v1/balances', params)
        return data

    def get_balances(self):
        params = {}
        data = self._post_data_auth('/v1/balances', params)

        if data is None:
            return []

        def standardize(d):
            return {
                'exchange': self.name,
                'asset': d['currency'],
                'balance': float(d['amount'])
            }
        return filter(
            lambda x: x['balance'] > 0.0,
            [standardize(x) for x in data]
        )

    def get_trades(self, pair):
        params = {
            'symbol': pair.upper(),
            'timestamp': 0,
            'limit_trades': 500
        }
        out = []
        while True:
            data = self._post_data_auth('/v1/mytrades', params)
            if data is None or len(data) == 0:
                return out
            out.extend(reversed(data))
            params['timestamp'] = data[0]['timestamp'] + 1
