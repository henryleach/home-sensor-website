import os
import configparser
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app(test_config=None):
    # create and configure the app in an
    # app factory
    app = Flask(__name__, instance_relative_config=False)

    # Default values while testing
    app.config.from_mapping(
        DATABASE=("tests/example-db.sqlite3"),
        DEFAULT_STATIONS=["Outside"],
        PROXY_LEVELS=0
    )

    if test_config is None:
        # load the config if it exists
        app.config.from_pyfile("config.py", silent=True)
    else:
        # or if provided the test config.
        app.config.from_mapping(test_config)


    print(app.config["DATABASE"])
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    pls = int(app.config["PROXY_LEVELS"])
    
    if pls > 0:
        # Set the right proxy level when behind something like nginx
        app.wsgi_app = ProxyFix(app.wsgi_app,
                                x_for=pls,
                                x_proto=pls,
                                x_host=pls,
                                x_prefix=pls)
    
    from . import db
    db.init_app(app)

    from . import overview, history
    app.register_blueprint(overview.bp)
    app.add_url_rule("/", endpoint="overview")

    app.register_blueprint(history.bp)
    app.add_url_rule("/history", endpoint="history")
    
    return app

