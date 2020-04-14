from flask import Flask
from flask_babel import Babel

babel = Babel()

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        BABEL_DEFAULT_LOCALE="fr",
        BABEL_DEFAULT_TIMEZONE="Europe/Vienna",
        SECRET_KEY="dev",
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    babel.init_app(app)
    from .views import program
    app.register_blueprint(program.bp)
    app.add_url_rule("/", endpoint="index")

    return app
