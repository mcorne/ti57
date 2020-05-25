from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = "123456"  # No need for secrecy here!
    from .views import program

    app.register_blueprint(program.bp)
    app.add_url_rule("/", endpoint="index")

    return app
