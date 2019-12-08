from app import app

from stock_margin import stock_margin_view


app.register_blueprint(stock_margin_view.bp)
