from flask import Flask, Blueprint, render_template, jsonify
from .bitfinex import BitfinexClient


def create_app(config_pyfile):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile(config_pyfile)
    bfx = BitfinexClient(app)
    blueprint = Blueprint(
        __name__+'bp',
        'bp',
        static_folder='static',
        template_folder='templates',
        url_prefix=app.config.get('URL_PREFIX')
    )
    @blueprint.route('/')
    def portfolio():
        return render_template('portfolio.html')

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
    app.register_blueprint(blueprint)
    return app
