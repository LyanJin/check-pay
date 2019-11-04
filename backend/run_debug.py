"""
单步调试
"""
import os
import config
from app.app import FlaskApp

os.environ['FLASK_SERVICE'] = 'backoffice'
# os.environ['FLASK_SERVICE'] = 'cashier'
# os.environ['FLASK_SERVICE'] = 'scheduler'
# os.environ['FLASK_SERVICE'] = 'gateway'

flask_app = FlaskApp.create_app(config.FLASK_SERVICE, config.FLASK_ENV)

if __name__ == '__main__':
    flask_app.run(host="0.0.0.0", port=6082)
