from flask import Flask

app = Flask(__name__,
            static_url_path='',
            static_folder='static'
            )

import country_database
import country_database_m2
import stock_index
import stock_pe
import stock_money_flow
import stock_margin
import stock_hold
import stock_finance
import stock
import stock_choose


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()


