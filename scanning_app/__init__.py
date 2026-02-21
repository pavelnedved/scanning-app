from flask import Flask
from dotenv import load_dotenv


def create_app(config_override: dict | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)

    if config_override:
        app.config.update(config_override)

    from .routes import bp
    app.register_blueprint(bp)

    return app
