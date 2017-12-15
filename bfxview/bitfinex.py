import requests  # pip install requests
import json
import base64
import hashlib
import hmac
import time #for nonce

class BitfinexClient(object):
    BASE_URL = "https://api.bitfinex.com/"

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.extensions['bitfinex'] = self
        self.api_key = app.config['BITFINEX_API_KEY']
        self.api_secret = app.config['BITFINEX_API_SECRET']

    def _nonce(self):
        """
        Returns a nonce
        Used in authentication
        """
        return str(int(round(time.time() * 1000)))

    def _headers(self, path, nonce, body):
        signature = "/api/" + path + nonce + body
        h = hmac.new(self.api_secret, signature, hashlib.sha384)
        signature = h.hexdigest()

        return {
            "bfx-nonce": nonce,
            "bfx-apikey": self.api_key,
            "bfx-signature": signature,
            "content-type": "application/json"
        }

    def _post_data_auth(self, path):
        nonce = self._nonce()
        body = {}
        rawBody = json.dumps(body)
        # path = "v2/auth/r/orders"
        headers = self._headers(path, nonce, rawBody)
        r = requests.post(
            self.BASE_URL + path,
            headers=headers,
            data=rawBody,
            verify=True
        )

        if r.status_code == 200:
          return r.json()

    def _get_data(self, path):
        r = requests.get(self.BASE_URL + path)
        if r.status_code == 200:
            return r.json()

    def _get_ticker(self, ticker):
        path = 'v2/ticker/t' + ticker
        fields = [
            'BID',
            'BID_SIZE',
            'ASK',
            'ASK_SIZE',
            'DAILY_CHANGE',
            'DAILY_CHANGE_PERC',
            'LAST_PRICE',
            'VOLUME',
            'HIGH',
            'LOW'
        ]
        data = self._get_data(path)
        if data:
            return dict(zip(fields, data))

    def _get_usd_rate(self, currency):
        if currency == 'USD':
            return 1
        try:
            return self._get_ticker(currency+'USD')['LAST_PRICE']
        except:
            pass
        try:
            return self._get_ticker(currency+'BTC')['LAST_PRICE'] * \
                self._get_ticker('BTCUSD')['LAST_PRICE']
        except:
            pass
        try:
            return self._get_ticker(currency+'ETH')['LAST_PRICE'] * \
                self._get_ticker('ETHUSD')['LAST_PRICE']
        except:
            pass

    @property
    def wallets(self):
        fields = [
            'WALLET_TYPE',
            'CURRENCY',
            'BALANCE',
            'UNSETTLED_INTEREST',
            'BALANCE_AVAILABLE'
        ]
        data = self._post_data_auth('v2/auth/r/wallets')
        if data:
            wlts = [dict(zip(fields, x)) for x in data]
            for w in wlts:
                w['USD_PRICE'] = self._get_usd_rate(w['CURRENCY'])
                w['USD_VALUE'] = w['USD_PRICE'] * w['BALANCE']
            return wlts

