from app import app

from country_database import country_database_view


app.register_blueprint(country_database_view.bp)