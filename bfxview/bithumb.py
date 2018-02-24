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

class BithumbClient(object):
    BASE_URL = "https://api.bithumb.com"

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.name = 'bithumb'
        app.extensions[self.name] = self
        self.api_key = app.config[self.name.upper()+'_API_KEY']
        self.api_secret = app.config[self.name.upper()+'_API_SECRET']

    def _timestamp(self):
        return str(int(round(time.time() * 1000)))

    def _post_data_auth(self, path, params):
        params['endpoint'] = path
        nonce = self._timestamp()
        string = path + chr(0) + urlencode(params) + chr(0) + nonce
        h = hmac.new(self.api_secret, string, hashlib.sha512)
        signature = base64.b64encode(h.hexdigest())
        headers = {
            'Api-Key': self.api_key,
            'Api-Sign': signature,
            'Api-Nonce': nonce
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
        params = {'currency': 'ALL'}
        data = self._post_data_auth('/info/balance', params)
        return data

    def get_balances(self):
        params = {'currency': 'ALL'}
        data = self._post_data_auth('/info/balance', params)['data']

        bal_ = [
            {
                'exchange': self.name,
                'asset': x.replace('total_', '').upper(),
                'balance': float(data[x])
            }
            for x in data.keys() if x.startswith('total_')
        ]
        return filter(lambda x: x['balance'] > 0.0, bal_)

    def get_trades(self, currency):
        params = {
            'currency': currency,
            'offset': 0,
            'count': 50,
            'searchGb': 0
            }
        out = []
        while True:
            data = self._post_data_auth('/info/user_transactions', params)['data']
            if data is None or len(data) == 0:
                return out
            out.extend(data)
            params['offset'] += len(data)
