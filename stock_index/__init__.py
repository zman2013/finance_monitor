from app import app

from stock_index import index_view


app.register_blueprint(index_view.bp)