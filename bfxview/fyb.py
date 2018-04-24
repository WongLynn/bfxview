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

class FybClient(object):
    BASE_URL = "https://www.fybsg.com/api/SGD"

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.name = 'fyb'
        app.extensions[self.name] = self
        self.api_key = app.config[self.name.upper()+'_API_KEY']
        self.api_secret = app.config[self.name.upper()+'_API_SECRET']

    def _timestamp(self):
        return str(int(round(time.time())))

    def _post_data_auth(self, path, params):
        params['timestamp'] = self._timestamp()
        payload = urlencode(params)
        h = hmac.new(self.api_secret, payload, hashlib.sha1)
        signature = h.hexdigest()
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'key': self.api_key,
            'sig': signature
        }

        r = requests.post(
            self.BASE_URL + path,
            headers=headers,
           data=payload
        )
        if r.status_code == 200:
            return r.content
        return r

    @property
    def test(self):
        params = {}
        data = self._post_data_auth('/test', params)
        return data

    def get_account_info(self):
        params = {}
        data = self._post_data_auth('/getaccinfo', params)
        return data

    def get_order_history(self):
        params = {'limit': 20}
        data = self._post_data_auth('/getorderhistory', params)
        return data
