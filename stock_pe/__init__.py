from app import app

from stock_pe import pe_view


app.register_blueprint(pe_view.bp)