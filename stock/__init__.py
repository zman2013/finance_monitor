from app import app

from stock import stock_view


app.register_blueprint(stock_view.bp)