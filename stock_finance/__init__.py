from app import app

from stock_finance import stock_finance_view


app.register_blueprint(stock_finance_view.bp)