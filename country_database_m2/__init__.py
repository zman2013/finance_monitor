from app import app

from country_database_m2 import country_database_m2_view


app.register_blueprint(country_database_m2_view.bp)