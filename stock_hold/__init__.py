from app import app

from stock_hold import stock_hold_view


app.register_blueprint(stock_hold_view.bp)