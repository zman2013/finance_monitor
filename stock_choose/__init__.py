from app import app

from stock_choose import stock_choose_view


app.register_blueprint(stock_choose_view.bp)