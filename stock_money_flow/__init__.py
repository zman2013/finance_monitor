from app import app

from stock_money_flow import stock_money_flow_view


app.register_blueprint(stock_money_flow_view.bp)