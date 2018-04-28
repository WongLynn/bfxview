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

    def _post_data_auth(self, path, params={}):
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
        return r

    def _post_data(self, path, params={}):
        for k in params.keys():
            if params[k] is None:
                del params[k]
        payload = urlencode(params)
        p = payload and ('?' + payload)
        r = requests.post(
            self.BASE_URL + path + p,
            data=payload
        )
        return r
    
    #### Private Endpoints ####
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

    def get_pending_orders(self):
        data = self._post_data_auth('/getpendingorders')
        return data

    def cancel_pending_orders(self, orderNo=None):
        params = {'orderNo': orderNo}
        data = self._post_data_auth('/cancelpendingorder', params)
        return data

    def place_order(self, qty, price, side):
        assert side in ['B', 'S'], 'side has to be either "B" or "S"'
        params = {
            'qty': qty,
            'price': price,
            'type': side
        }
        data = self._post_data_auth('/placeorder', params)
        return data
    
    #### Public Endpoints ###
    def get_ticker(self):
        return self._post_data('/ticker.json')

    def get_ticker_details(self):
        return self._post_data('/tickerdetailed.json')
    
    def get_order_book(self):
        return self._post_data('/orderbook.json')

    def get_trades(self, since=None):
        params = {'since': since}
        return self._post_data('/trades.json', params)
