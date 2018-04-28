from flask import Flask, Blueprint, render_template, jsonify
from datetime import datetime
from .bitfinex import BitfinexClient
from .binance_ex import BinanceClient
from .bithumb import BithumbClient
from .gateio import GateIOClient
from .gemini import GeminiClient
from .fyb import FybClient


def create_app(config_pyfile):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile(config_pyfile)
    bfx = BitfinexClient(app)
    exchanges = [
        bfx,
        BinanceClient(app),
        BithumbClient(app),
        GateIOClient(app),
        GeminiClient(app)
    ]
    blueprint = Blueprint(
        __name__+'bp',
        'bp',
        static_folder='static',
        template_folder='templates',
        url_prefix=app.config.get('URL_PREFIX')
    )
    @blueprint.route('/')
    def portfolio():
        return render_template('portfolio.html', bch_table=get_bch_table())

    def get_bch_table():
        p_BCH = bfx._get_ticker('BCHUSD')['LAST_PRICE']
        p_EOS = bfx._get_ticker('EOSUSD')['LAST_PRICE']
        p_OMG = bfx._get_ticker('OMGUSD')['LAST_PRICE']
        t_EOS = 346.3188534
        t_OMG = 221.5694933
        data = [{
            'bch_price': p_BCH,
            'token': 'EOS',
            'original_tokens': 724.9880885,
            'bought_bch': 2.09341213,
            'token_price': p_EOS,
            'target': t_EOS
        },{
            'bch_price': p_BCH,
            'token': 'OMG',
            'original_tokens': 129.883,
            'bought_bch': 0.58619532,
            'token_price': p_OMG,
            'target': t_OMG,
        }]
        for item in data:
            item['bch_price_in_token'] = item['bch_price'] / item['token_price']
            item['delta'] = item['bch_price_in_token'] - item['target']
            item['token_delta'] = item['bought_bch'] * item['bch_price'] / \
                item['token_price'] - item['original_tokens']
        return data

    @blueprint.route('/data')
    def data():
        return jsonify([
            {
                'label': x['CURRENCY'],
                'value': x['USD_VALUE'],
                'price': x['USD_PRICE'],
                'balance': x['BALANCE']
            }
            for x in bfx.wallets
        ])

    @blueprint.route('/balances')
    def balances():
        timestamp = str(datetime.utcnow())
        def append_timestamp(d):
            d['timestamp'] = timestamp
            return d
        bal_ = [
            append_timestamp(d)
            for e in exchanges
            for d in e.get_balances()
        ]
        return jsonify(bal_)

    @blueprint.route('/trades/<exchange>/<pair>')
    def trades(exchange, pair):
        if exchange not in app.extensions:
            return jsonify({
                'message': 'Invalid Exchange %s.' % exchange
            })
        if not hasattr(app.extensions[exchange], 'get_trades'):
            return jsonify({
                'message': 'Cannot Get Trades for Exchange %s.' % exchange
            })
        out = app.extensions[exchange].get_trades(pair)
        return jsonify(out)

    @blueprint.route('/transfers/<exchange>')
    def transfers(exchange):
        if exchange not in app.extensions:
            return jsonify({
                'message': 'Invalid Exchange %s.' % exchange
            })
        if not hasattr(app.extensions[exchange], 'get_transfers'):
            return jsonify({
                'message': 'Cannot Get Trades for Exchange %s.' % exchange
            })
        out = app.extensions[exchange].get_transfers()
        return jsonify(out)

    app.register_blueprint(blueprint)
    return app