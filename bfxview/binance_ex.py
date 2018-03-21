import requests  # pip install requests
import json
import base64
import hashlib
import hmac
try:
    from urllib.parse import quote
except:
    from urllib import quote
import time #for nonce
from binance.client import Client

class BinanceClient(object):

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.name = 'binance'
        app.extensions[self.name] = self
        self.api_key = app.config[self.name.upper()+'_API_KEY']
        self.api_secret = app.config[self.name.upper()+'_API_SECRET']
        self.client = Client(self.api_key, self.api_secret)

    def get_balances(self):

        def append_total(d):
            d['total'] = float(d['free']) + float(d['locked'])
            return d

        def standardize(d):
            return {
                'exchange': self.name,
                'asset': d['asset'],
                'balance': d['total']
            }
        return filter(
            lambda x: x['balance'] > 0.0,
            [standardize(append_total(x)) for x in self.client.get_account()['balances']]
        )

    def get_trades(self, pair):
        params = {
            'symbol': pair.upper(),
            'fromId': 0
        }
        out = []
        while True:
            data = self.client.get_my_trades(**params)
            if data is None or len(data) == 0:
                return out
            out.extend(data)
            params['fromId'] = data[-1]['id'] + 1

    def get_transfers(self):
        def with_type(item, type):
            item['type'] = type
            return item
        out = []
        data = self.client.get_deposit_history()
        if data and 'depositList' in data:
            out.extend([
                with_type(item, 'Deposit')
                for item in data['depositList']
            ])
        data = self.client.get_withdraw_history()
        if data and 'withdrawList' in data:
            out.extend([
                with_type(item, 'Withdraw')
                for item in data['withdrawList']
            ])
        return out
